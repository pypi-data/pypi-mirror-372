"""
# Author: Yuhan Fei & Jiasheng Zhang
# Created Time :  15 May 2021
# Revised Time v0:  12 May 2023
# Revised Time v1:  22 Feb 2024
# Revised Time v2:  29 May 2024
"""

import torch
import torch.nn.functional as F
from torch import nn
from smrtnet.transformers import EsmModel as pretrain_bert
from smrtnet.transformers import EsmConfig
from smrtnet.LM_Mol.tokenizer import MolTranBertTokenizer
from smrtnet.LM_Mol.rotate_builder import RotateEncoderBuilder as rotate_builder
from smrtnet.fast_transformers.feature_maps import GeneralizedRandomFeatures
from smrtnet.fast_transformers.masking import LengthMask as LM
from functools import partial

device = torch.device('cuda' if torch.cuda.is_available() else 'cuda')


class AttentionBlock(nn.Module):
    """ A class for attention mechanisn with QKV attention """
    def __init__(self, hid_dim, n_heads, dropout):
        super().__init__()

        self.hid_dim = hid_dim
        self.n_heads = n_heads

        assert hid_dim % n_heads == 0

        self.f_q = nn.Linear(hid_dim, hid_dim)
        self.f_k = nn.Linear(hid_dim, hid_dim)
        self.f_v = nn.Linear(hid_dim, hid_dim)

        self.fc = nn.Linear(hid_dim, hid_dim)

        self.do = nn.Dropout(dropout)

        self.scale = torch.sqrt(torch.FloatTensor([hid_dim // n_heads])).cuda()

    def forward(self, query, key, value, mask=None):


        batch_size = query.shape[0]
        Q = self.f_q(query)
        K = self.f_k(key)
        V = self.f_v(value)

        Q = Q.view(batch_size, self.n_heads, self.hid_dim // self.n_heads).unsqueeze(3)
        K = K.view(batch_size, self.n_heads, self.hid_dim // self.n_heads).unsqueeze(3)
        K_T = K.view(batch_size, self.n_heads, self.hid_dim // self.n_heads).unsqueeze(3).transpose(2,3)
        V = V.view(batch_size, self.n_heads, self.hid_dim // self.n_heads).unsqueeze(3)

        #energy = torch.mul(Q, K)
        energy = torch.matmul(Q, K_T) / self.scale

        if mask is not None:
            energy = energy.masked_fill(mask == 0, -1e10)

        attention = self.do(F.softmax(energy, dim=-1))

        weighter_matrix = torch.matmul(attention, V)

        weighter_matrix = weighter_matrix.permute(0, 2, 1, 3).contiguous()

        weighter_matrix = weighter_matrix.view(batch_size, self.n_heads * (self.hid_dim // self.n_heads))

        weighter_matrix = self.do(self.fc(weighter_matrix))

        return weighter_matrix



class lm_layer(nn.Module):
    def __init__(self, n_embd, n_vocab):
        super().__init__()
        self.embed = nn.Linear(n_embd, n_embd)
        self.ln_f = nn.LayerNorm(n_embd)
        self.head = nn.Linear(n_embd, n_vocab, bias=False)

    def forward(self, tensor):
        tensor = self.embed(tensor)
        tensor = F.gelu(tensor)
        tensor = self.ln_f(tensor)
        tensor = self.head(tensor)
        return tensor


class Conv2d(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size, stride=1, relu=True, same_padding=False, bn=False):
        super(Conv2d, self).__init__()
        p0 = int((kernel_size[0] - 1) / 2) if same_padding else 0
        p1 = int((kernel_size[1] - 1) / 2) if same_padding else 0
        padding = (p0, p1)
        self.conv = nn.Conv2d(in_channels, out_channels, kernel_size, stride, padding=padding)
        self.bn = nn.BatchNorm2d(out_channels) if bn else None
        self.relu = nn.ReLU(inplace=True) if relu else None

    def forward(self, x):
        x = self.conv(x)
        if self.bn is not None:
            x = self.bn(x)
        if self.relu is not None:
            x = self.relu(x)
        return x


class SEBlock(nn.Module):
    def __init__(self, channel, reduction=2):
        super(SEBlock, self).__init__()
        self.avg_pool = nn.AdaptiveAvgPool2d(1)
        self.fc = nn.Sequential(
            nn.Linear(channel, channel // reduction),
            nn.ReLU(inplace=True),
            nn.Linear(channel // reduction, channel),
            nn.Sigmoid()
        )

    def forward(self, x):
        b, c, _, _ = x.size()
        y = self.avg_pool(x).view(b, c)
        y = self.fc(y).view(b, c, 1, 1)
        return y


class ResidualBlock1D(nn.Module):

    def __init__(self, planes, downsample=True):
        super(ResidualBlock1D, self).__init__()
        self.c1 = nn.Conv1d(planes, planes, kernel_size=1, stride=1, bias=False)
        self.b1 = nn.BatchNorm1d(planes)
        self.c2 = nn.Conv1d(planes, planes * 2, kernel_size=11, stride=1, padding=5, bias=False)
        # self.c2 = nn.Conv1d(planes,   planes*2, kernel_size=7, stride=1,padding=3, bias=False)
        self.b2 = nn.BatchNorm1d(planes * 2)
        self.c3 = nn.Conv1d(planes * 2, planes * 8, kernel_size=1, stride=1, bias=False)
        self.b3 = nn.BatchNorm1d(planes * 8)
        self.downsample = nn.Sequential(
            nn.Conv1d(planes, planes * 8, kernel_size=1, stride=1, bias=False),
            nn.BatchNorm1d(planes * 8),
        )
        self.relu = nn.ReLU(inplace=True)

    def forward(self, x):
        identity = x

        out = self.c1(x)
        out = self.b1(out)
        out = self.relu(out)

        out = self.c2(out)
        out = self.b2(out)
        out = self.relu(out)

        out = self.c3(out)
        out = self.b3(out)

        if self.downsample:
            identity = self.downsample(x)

        out += identity
        out = self.relu(out)
        return out

class ResidualBlock2D(nn.Module):

    def __init__(self, planes, kernel_size=(7, 4), padding=(3, 1), downsample=True):
        super(ResidualBlock2D, self).__init__()
        self.c1 = nn.Conv2d(planes, planes, kernel_size=1, stride=1, bias=False)
        self.b1 = nn.BatchNorm2d(planes)
        self.c2 = nn.Conv2d(planes, planes * 2, kernel_size=kernel_size, stride=1,
                            padding=padding, bias=False)
        self.b2 = nn.BatchNorm2d(planes * 2)
        self.c3 = nn.Conv2d(planes * 2, planes * 4, kernel_size=1, stride=1, bias=False)
        self.b3 = nn.BatchNorm2d(planes * 4)
        self.downsample = nn.Sequential(
            nn.Conv2d(planes, planes * 4, kernel_size=1, stride=1, bias=False),
            nn.BatchNorm2d(planes * 4),
        )
        self.relu = nn.ReLU(inplace=True)

    def forward(self, x):
        identity = x

        out = self.c1(x)
        out = self.b1(out)
        out = self.relu(out)

        out = self.c2(out)
        out = self.b2(out)
        out = self.relu(out)

        out = self.c3(out)
        out = self.b3(out)

        if self.downsample:
            identity = self.downsample(x)
        # print(out.shape,identity.shape)
        out += identity
        out = self.relu(out)

        return out


class SmrtNet(nn.Module):

    def __init__(self, args):
        super(SmrtNet, self).__init__()
        ## parameters
        self.args = args
        self.input_dim_drug = args.hidden_dim_graph
        self.input_dim_target = args.hidden_dim_rna
        self.hidden_dims = args.cls



        self.input_dim_rna_lm = args.hidden_dim_rna_lm
        self.input_dim_mol_lm = args.hidden_dim_mol_lm
        layer_size = len(self.hidden_dims) + 1

        self.output_dim = self.input_dim_drug + self.input_dim_target + self.input_dim_rna_lm + self.input_dim_mol_lm
        self.output_dim_lm = self.input_dim_rna_lm

        dims = [self.output_dim] + self.hidden_dims + [1]

        if args.mode == "SEQ":
            h_p, h_k = 1, 3
            self.n_features = 4
        elif args.mode == "SPU":
            h_p, h_k = 2, 5
            self.n_features = 5
        elif args.mode == "PU":
            h_p, h_k = 1, 3
            self.n_features = 3


        ## drug graph network
        from dgllife.model.gnn.gat import GAT
        from dgllife.model.readout.weighted_sum_and_max import WeightedSumAndMax
        self.gnn = GAT(in_feats=args.gnn_in_feats,
                        hidden_feats=[args.gnn_hid_dim_drug] * args.gnn_num_layers,
                        num_heads=[args.gat_num_heads] * args.gnn_num_layers,
                        feat_drops=[args.gat_feat_drops] * args.gnn_num_layers,
                        attn_drops=[args.gat_attn_drops] * args.gnn_num_layers,
                        alphas=[0.2] * args.gnn_num_layers,
                        residuals=[True] * args.gnn_num_layers,
                        agg_modes=['flatten'] * args.gnn_num_layers, #mean
                        activations=[F.relu] * args.gnn_num_layers,
                        biases=[None] * args.gnn_num_layers  # True
                        )

        gnn_out_feats = self.gnn.hidden_feats[-1] * self.gnn.num_heads[-1]
        self.readout = WeightedSumAndMax(gnn_out_feats)
        self.transform = nn.Linear(self.gnn.hidden_feats[-1] * 2 * self.gnn.num_heads[-1], args.hidden_dim_graph)

    
        ## pretrained RNA model

        self.mid_dim_bert = 768
        configuration_pretrain = EsmConfig.from_pretrained(args.lm_rna_config)

        self.pretrain_bert = pretrain_bert(configuration_pretrain)

        dict_para_pretrain = torch.load(args.lm_rna_model, map_location=torch.device('cuda:'+str(args.cuda)))

        for name_, para_ in self.pretrain_bert.state_dict().items():
            if 'esm.' + name_ in dict_para_pretrain.keys():
                self.pretrain_bert.state_dict()[name_].copy_(dict_para_pretrain['esm.' + name_])
        for para in self.pretrain_bert.parameters():
            if 'rnalm' in args.lm_ft:
                para.requires_grad = True
            else:
                para.requires_grad = False

        self.mlp_l1 = nn.Linear(640, 512)
        self.mlp_l2 = nn.Linear(512, 128)
        self.mlp_l3 = nn.Linear(3968, 1024)
        self.mlp_l4 = nn.Linear(1024, self.input_dim_rna_lm) 

        kernal = args.kernal
        pad = args.pad
        base_channel = args.channel

        self.conv = Conv2d(1, base_channel, kernel_size=(kernal, h_k), bn=True, same_padding=True)
        self.se = SEBlock(base_channel)
        self.res2d = ResidualBlock2D(base_channel, kernel_size=(kernal, h_k), padding=(pad, h_p))  #
        self.res1d = ResidualBlock1D(base_channel * 4)
        self.avgpool = nn.AvgPool2d((1, self.n_features))
        self.gpool = nn.AdaptiveAvgPool1d(1)
        self.fct = nn.Linear(base_channel * 4 * 8, self.input_dim_target)

        ###dropout
        self.dropout = nn.Dropout(0.1)

        import pkg_resources
        file_path = pkg_resources.resource_filename(__name__, "LM_Mol/bert_vocab.txt")
        tokenizer = MolTranBertTokenizer(file_path)
        n_vocab = len(tokenizer.vocab)
        self.tok_emb = nn.Embedding(n_vocab, 768)
        self.drop_molformer = nn.Dropout(0.1)
        builder = rotate_builder.from_kwargs(
            n_layers=12,
            n_heads=12,
            query_dimensions=768 // 12,
            value_dimensions=768 // 12,
            feed_forward_dimensions=768,
            attention_type='linear',
            #attention_type='full',
            feature_map=partial(GeneralizedRandomFeatures, n_dims=32),
            activation='gelu',
        )
        self.blocks = builder.get()
        self.lang_model = lm_layer(768, n_vocab)

        mol_para_pretrain = torch.load(args.lm_mol_model, map_location=torch.device('cuda:'+str(args.cuda)))
        mol_para_pretrain = mol_para_pretrain['state_dict']

        for name_, para_ in self.blocks.state_dict().items():
            if 'blocks.' + name_ in mol_para_pretrain.keys():
                self.blocks.state_dict()[name_].copy_(mol_para_pretrain['blocks.' + name_])
        for name_, para_ in self.tok_emb.state_dict().items():
            if 'tok_emb.' + name_ in mol_para_pretrain.keys():
                self.tok_emb.state_dict()[name_].copy_(mol_para_pretrain['tok_emb.' + name_])
        for name_, para_ in self.lang_model.state_dict().items():
            if 'lang_model.' + name_ in mol_para_pretrain.keys():
                self.lang_model.state_dict()[name_].copy_(mol_para_pretrain['lang_model.' + name_])

        self.mlp_vDs = nn.Linear(768, self.input_dim_mol_lm)
        self.mlp_d1 = nn.Linear(768, self.input_dim_mol_lm)  # 31
        self.mlp_d2 = nn.Linear(16384, self.input_dim_mol_lm)  # 31

        for para in self.blocks.parameters():
            if 'molformer' in args.lm_ft:
                para.requires_grad = True
            else:
                para.requires_grad = False

        self.LN1 = nn.LayerNorm(self.output_dim_lm)
        self.LN2 = nn.LayerNorm(self.output_dim_lm)
        self.LN3 = nn.LayerNorm(self.output_dim_lm)
        self.LN4 = nn.LayerNorm(self.output_dim_lm)
        self.LN5 = nn.LayerNorm(self.output_dim_lm)
        self.LN6 = nn.LayerNorm(self.output_dim_lm)
        self.LN7 = nn.LayerNorm(self.output_dim_lm)
        self.LN8 = nn.LayerNorm(self.output_dim_lm)
        self.LN9 = nn.LayerNorm(self.output_dim_lm*2)
        self.LN10 = nn.LayerNorm(self.output_dim_lm*2)
        self.BN = nn.BatchNorm1d(self.output_dim_lm*4)
        self.attentionBlock1 = AttentionBlock(self.output_dim_lm, 2, 0.1)
        self.attentionBlock2 = AttentionBlock(self.output_dim_lm, 2, 0.1)
        self.attentionBlock3 = AttentionBlock(self.output_dim_lm, 2, 0.1)
        self.attentionBlock4 = AttentionBlock(self.output_dim_lm, 2, 0.1)
        self.attentionBlock5 = AttentionBlock(self.output_dim_lm*4, 8, 0.3)
        self.attentionBlock6 = AttentionBlock(self.output_dim_lm*2, 2, 0.1)
        self.attentionBlock7 = AttentionBlock(self.output_dim_lm*2, 2, 0.1)
        dims = [self.output_dim_lm*4] + self.hidden_dims[1:] + [1]
        layer_size = layer_size - 1

        ###Fully-connected
        self.fc = nn.ModuleList([nn.Linear(dims[i], dims[i + 1]) for i in range(layer_size)])

    def forward(self, v_D, de_idx, de_mask, v_P, re_input_ids, re_atten_mask, get_attention=False):

        feats = v_D.ndata['h']
        node_feats = self.gnn(v_D, feats)
        graph_feats = self.readout(v_D, node_feats)
        v_D = self.transform(graph_feats)

        if get_attention:
            node_feats.retain_grad()

        token_embeddings = self.tok_emb(de_idx.long())  # each index maps to a (learnable) vector
        if get_attention:
            token_embeddings.retain_grad()

        v_De = self.drop_molformer(token_embeddings)
        v_De = self.blocks(v_De, length_mask=LM(de_mask.sum(-1)))

        v_De = F.dropout(self.mlp_d1(v_De), 0.1, training=self.training)
        v_De = v_De.view(v_De.shape[0], v_De.shape[2], v_De.shape[1]) 
        m = torch.nn.AdaptiveMaxPool1d(128)
        v_De = m(v_De) 
        v_De = v_De.view(v_De.shape[0], v_De.shape[2] * v_De.shape[1]) 
        v_De = F.dropout(self.mlp_d2(v_De), 0.1, training=self.training)

        v_Pe, v_Pe_embeddings = self.pretrain_bert(**{'input_ids': re_input_ids.long(), 'attention_mask':re_atten_mask})
        if get_attention:
            v_Pe_embeddings.retain_grad()

        v_Pe = v_Pe.last_hidden_state
        v_Pe = v_Pe[:, 1:, :]

        v_Pe = F.dropout(self.mlp_l1(v_Pe), 0.3, training=self.training)
        v_Pe = F.dropout(self.mlp_l2(v_Pe), 0.1, training=self.training) 
        v_Pe = v_Pe.view(v_Pe.shape[0], v_Pe.shape[1]* v_Pe.shape[2]) 
        v_Pe = F.dropout(self.mlp_l3(v_Pe), 0.3, training=self.training)
        v_Pe = F.dropout(self.mlp_l4(v_Pe), 0.1, training=self.training) 

        x = self.conv(v_P)
        x = F.dropout(x, 0.1, training=self.training)
        z = self.se(x)
        x = self.res2d(z * x)
        x = F.dropout(x, 0.5, training=self.training)
        x = self.avgpool(x)
        x = x.view(x.shape[0], x.shape[1], x.shape[2])
        x = self.res1d(x)
        x = F.dropout(x, 0.3, training=self.training)
        x = self.gpool(x)
        x = x.view(x.shape[0], x.shape[1])
        v_P = self.fct(x)

        v_Pe, v_De, v_P, v_D = self.LN1(v_Pe), self.LN2(v_De), self.LN3(v_P), self.LN4(v_D)
        CAB_g1 = v_Pe + self.attentionBlock1(v_Pe, v_De, v_De)
        CAB_l1 = v_P + self.attentionBlock2(v_P, v_D, v_D)
        CAB_g2 = v_De + self.attentionBlock3(v_De, v_Pe, v_Pe)
        CAB_l2 = v_D + self.attentionBlock4(v_D, v_P, v_P)
        CAB_g1, CAB_g2, CAB_l1, CAB_l2= self.LN5(CAB_g1), self.LN6(CAB_g2), self.LN7(CAB_l1), self.LN8(CAB_l2)
        
        v_f1 = torch.cat((CAB_g1, CAB_g2), 1)
        v_f2 = torch.cat((CAB_l1, CAB_l2), 1)
    
        v_f1 = v_f1 + self.attentionBlock6(v_f1, v_f1, v_f1)
        v_f2 = v_f2 + self.attentionBlock7(v_f2, v_f2, v_f2)

        v_f1n, v_f2n = self.LN9(v_f1), self.LN10(v_f2)

        v_f = torch.cat((v_f1n, v_f2n), 1)
        v_f = self.BN(v_f)
        v_f = v_f + self.attentionBlock5(v_f, v_f, v_f)


        for i, l in enumerate(self.fc):
            if i == (len(self.fc) - 1):
                v_f = l(v_f)
            else:
                v_f = F.relu(self.dropout(l(v_f)))
        if get_attention:
            return v_f, token_embeddings, v_Pe_embeddings, node_feats
        else:
            return v_f
