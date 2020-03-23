import torch
import torch.nn as nn
from transformer.Layers import EncoderLayer
from transformer.Embed import Embedder, PositionalEncoder
from transformer.Sublayers import Norm
import copy
import torch.nn.functional as F


def get_clones(module, N):
    return nn.ModuleList([copy.deepcopy(module) for i in range(N)])


class Encoder(nn.Module):
    def __init__(self, vocab_size, d_model, N, heads, dropout):
        super().__init__()
        self.N = N
        self.embed = Embedder(vocab_size, d_model)
        #self.pe = PositionalEncoder(d_model=47, max_seq_len=13,dropout=dropout)
        self.layers = get_clones(EncoderLayer(d_model, heads, dropout), N)
        self.norm = Norm(d_model)

    def forward(self, src, mask):
        #x = self.embed(src)
        x=src #[N, 13, 47] float32
        #x = self.pe(x) #Disable the positional encoder
        for i in range(self.N):
            x = self.layers[i](x, mask)
        return x

class EdgeClassify(nn.Module):
    def __init__(self, msp_len, max_atoms, d_model, num_bonds_prediction):
        super().__init__()
        self.ll = nn.Linear(msp_len, max_atoms)
        self.fl = nn.Linear(d_model * 2, num_bonds_prediction)

    def forward(self, e_output, max_atoms):
        # reduce_e = e_output.permute(0, 2, 1) #[N,13,d_mol]
        # #reduce_e = self.ll(reduce_e) #[bs, d_model=48, 13]
        # #reduce_e = reduce_e.permute(0, 2, 1) # reduce to target output [bs, 13, d_model]
        # reduce_e = reduce_e.unsqueeze(2) # Shape: (batch, max_atoms, 1, e_out_dim) [bt,13,1,d_m]
        # repeat_e = reduce_e.repeat(1, 1, max_atoms, 1) # (batch, max_atoms, max_atoms, e_out_dim) [bt,13,13,d_m]
        # final_e = torch.tensor((), dtype=torch.float32)
        # final_e = final_e.new_ones((repeat_e.shape[0], repeat_e.shape[1], repeat_e.shape[2], 2 * repeat_e.shape[3])) #[bt,13,13,d_m*2]
        # for i in range(max_atoms):
        #     add_extra = repeat_e[:, i, i, :] # (batch, e_out_dim) [bt,512]
        #     add_extra = add_extra.unsqueeze(1) # (batch, 1, e_out_dim)
        #     add_extra = add_extra.repeat(1, max_atoms, 1) # (batch, max_atoms, e_out_dim)
        #     final_e[:, i, :, :] = torch.cat((repeat_e[:, :, i, :], add_extra), 2)
        # final_e = self.fl(final_e) #[8,13,13,4]
        # return final_e

        reduce_e = e_output.unsqueeze(2)  # Shape: (batch, max_atoms, 1, e_out_dim) [bt,13,1,d_m]
        repeat_e = reduce_e.repeat(1, 1, max_atoms, 1)  # (batch, max_atoms, max_atoms, e_out_dim) [bt,13,13,d_m]
        final_e = torch.tensor((), dtype=torch.float32)
        final_e = final_e.new_ones(
            (repeat_e.shape[0], repeat_e.shape[1], repeat_e.shape[2], 2 * repeat_e.shape[3]))  # [bt,13,13,d_m*2]
        for i in range(max_atoms):
            for j in range(max_atoms):
                final_e[:, i, j, :] = torch.cat((repeat_e[:, i, i, :], repeat_e[:, j, j, :]), dim=1)
            # add_extra = repeat_e[:, i, i, :] # (batch, e_out_dim) [bt,512]
            # add_extra = add_extra.unsqueeze(1) # (batch, 1, e_out_dim)
            # add_extra = add_extra.repeat(1, max_atoms, 1) # (batch, max_atoms, e_out_dim)
            # final_e[:, i, :, :] = torch.cat((repeat_e[:, i, :, :], add_extra), 2)
        final_e = self.fl(final_e)  # [8,13,13,4]
        return final_e

class EdgeClassify2(nn.Module):
    def __init__(self, msp_len, max_atoms, d_model, num_bonds_prediction):
        super().__init__()
        self.ll = nn.Linear(43, max_atoms)
        self.ll2 = nn.Linear(18, max_atoms)
        self.fl = nn.Linear(max_atoms * 2, num_bonds_prediction)

    def forward(self, e_output, max_atoms):
        # reduce_e = e_output.permute(0, 2, 1) #[N,13,d_mol]
        # #reduce_e = self.ll(reduce_e) #[bs, d_model=48, 13]
        # #reduce_e = reduce_e.permute(0, 2, 1) # reduce to target output [bs, 13, d_model]
        # reduce_e = reduce_e.unsqueeze(2) # Shape: (batch, max_atoms, 1, e_out_dim) [bt,13,1,d_m]
        # repeat_e = reduce_e.repeat(1, 1, max_atoms, 1) # (batch, max_atoms, max_atoms, e_out_dim) [bt,13,13,d_m]
        # final_e = torch.tensor((), dtype=torch.float32)
        # final_e = final_e.new_ones((repeat_e.shape[0], repeat_e.shape[1], repeat_e.shape[2], 2 * repeat_e.shape[3])) #[bt,13,13,d_m*2]
        # for i in range(max_atoms):
        #     add_extra = repeat_e[:, i, i, :] # (batch, e_out_dim) [bt,512]
        #     add_extra = add_extra.unsqueeze(1) # (batch, 1, e_out_dim)
        #     add_extra = add_extra.repeat(1, max_atoms, 1) # (batch, max_atoms, e_out_dim)
        #     final_e[:, i, :, :] = torch.cat((repeat_e[:, :, i, :], add_extra), 2)
        # final_e = self.fl(final_e) #[8,13,13,4]
        # return final_e

        reduce_e = self.ll2(e_output)  # [bs, 43,13]
        reduce_e = reduce_e.permute(0, 2, 1)  # [N,13,43]
        reduce_e = self.ll(reduce_e)  # [bs, 13,13]
        reduce_e = reduce_e.unsqueeze(2)  # Shape: (batch, max_atoms, 1, e_out_dim) [bt,13,1,d_m]
        repeat_e = reduce_e.repeat(1, 1, max_atoms, 1)  # (batch, max_atoms, max_atoms, e_out_dim) [bt,13,13,d_m]
        final_e = torch.tensor((), dtype=torch.float32)
        final_e = final_e.new_ones(
            (repeat_e.shape[0], repeat_e.shape[1], repeat_e.shape[2], 2 * repeat_e.shape[3]))  # [bt,13,13,d_m*2]
        for i in range(max_atoms):
            for j in range(max_atoms):
                final_e[:, i, j, :] = torch.cat((repeat_e[:, i, i, :], repeat_e[:, j, j, :]), dim=1)
            # add_extra = repeat_e[:, i, i, :] # (batch, e_out_dim) [bt,512]
            # add_extra = add_extra.unsqueeze(1) # (batch, 1, e_out_dim)
            # add_extra = add_extra.repeat(1, max_atoms, 1) # (batch, max_atoms, e_out_dim)
            # final_e[:, i, :, :] = torch.cat((repeat_e[:, i, :, :], add_extra), 2)
        final_e = self.fl(final_e)  # [8,13,13,4]
        return final_e

class EncoderEdgeClassify(nn.Module):
    def __init__(self, vocab_size, d_model, N, heads, dropout, msp_len, max_atoms, num_bonds_prediction):
        super().__init__()
        self.encoder = Encoder(vocab_size, d_model, N, heads, dropout)
        self.edge_classify = EdgeClassify2(msp_len, max_atoms, d_model, num_bonds_prediction)

    def forward(self, src, mask, max_atoms):
        output = self.encoder(src, mask) #[batch, 43, 18]
        output = self.edge_classify(output, max_atoms)
        return output
