"""
Multi-Scale PatchGAN Discriminator for Anime Reality AI.
Differentiates between generated anime images, real anime frames, and smooth edge regions.
"""

import torch
import torch.nn as nn


class PatchDiscriminator(nn.Module):
    """PatchGAN Discriminator with Spectral Norm for stable adversarial training."""
    def __init__(self, in_channels: int = 3, num_filters: int = 64, num_layers: int = 3):
        super().__init__()
        layers = [
            nn.utils.spectral_norm(nn.Conv2d(in_channels, num_filters, kernel_size=4, stride=2, padding=1)),
            nn.LeakyReLU(0.2, inplace=True)
        ]

        nf = num_filters
        for _ in range(1, num_layers):
            nf_prev = nf
            nf = min(nf * 2, 512)
            layers.extend([
                nn.utils.spectral_norm(nn.Conv2d(nf_prev, nf, kernel_size=4, stride=2, padding=1)),
                nn.InstanceNorm2d(nf),
                nn.LeakyReLU(0.2, inplace=True)
            ])

        layers.extend([
            nn.utils.spectral_norm(nn.Conv2d(nf, 1, kernel_size=4, stride=1, padding=1))
        ])

        self.model = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.model(x)
