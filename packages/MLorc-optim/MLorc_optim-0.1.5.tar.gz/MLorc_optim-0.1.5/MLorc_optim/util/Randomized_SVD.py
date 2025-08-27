import torch
from torch import Tensor

from typing import Tuple

def _rsvd(A: Tensor, rank: int, oversampling: int) -> Tuple[Tensor, Tensor, Tensor]:
        """Performs Randomized SVD."""
        device = A.device
        m, n = A.shape
        l = rank + oversampling
        true_rank = min(m, n, rank)
        A = A.float()

        if true_rank == 0:
            U = torch.zeros(m, rank, dtype=torch.float32, device=device)
            S = torch.zeros(rank, dtype=torch.float32, device=device)
            Vh = torch.zeros(rank, n, dtype=torch.float32, device=device)
            return U, S, Vh

        if l >= min(m, n):
            U_full, S_full, Vh_full = torch.linalg.svd(A.float(), full_matrices=False)
            U, S, Vh = U_full[:, :true_rank], S_full[:true_rank], Vh_full[:true_rank, :]
        else:
            Omega = torch.randn(n, l, dtype=torch.float32, device=device)
            Y = A.float() @ Omega
            Q, _ = torch.linalg.qr(Y.float())
            B = Q.T @ A
            U_tilde, S, Vh = torch.linalg.svd(B.float(), full_matrices=False)
            U, S, Vh = (Q @ U_tilde)[:, :true_rank], S[:true_rank], Vh[:true_rank, :]

        if true_rank < rank:
            U_padded = torch.zeros(m, rank, dtype=torch.float32, device=device)
            S_padded = torch.zeros(rank, dtype=torch.float32, device=device)
            Vh_padded = torch.zeros(rank, n, dtype=torch.float32, device=device)
            U_padded[:, :true_rank] = U
            S_padded[:true_rank] = S
            Vh_padded[:true_rank, :] = Vh
            U, S, Vh = U_padded, S_padded, Vh_padded

        return U, S, Vh