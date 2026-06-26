# UNet Architecture — From Scratch

## What this is

A from-scratch PyTorch implementation of the full UNet architecture (4 encoder blocks, bottleneck, 4 decoder blocks) with skip connections. This is a comprehension exercise, not a training run — the goal is to verify the shape arithmetic at every stage and understand why UNet concatenates (rather than adds) skip connections.

## What it covers

- EncoderBlock: two Conv2d+ReLU layers with padding=1 (preserves spatial dims), output saved as skip before MaxPool
- DecoderBlock: ConvTranspose2d(in_channels, in_channels//2, kernel_size=2, stride=2) simultaneously doubles spatial dims and halves channels, then concat with skip along dim=1, then two Conv2d+ReLU layers
- Full UNet: 4 encoder blocks + bottleneck + 4 decoder blocks + output conv
- Shape verification confirmed by forward pass with dummy input (1, 1, 256, 256) → (1, 1, 256, 256)
- Reflection: why UNet concatenates vs ResNet adds (semantic space incompatibility, not shape mismatch)

## Architecture

```
Input (B, 1, H, W)
    ↓
enc1 EncoderBlock(1, 64)    → skip4 (B, 64, H, W)     → MaxPool → (B, 64, H/2, W/2)
enc2 EncoderBlock(64, 128)  → skip3 (B, 128, H/2)      → MaxPool → (B, 128, H/4)
enc3 EncoderBlock(128, 256) → skip2 (B, 256, H/4)      → MaxPool → (B, 256, H/8)
enc4 EncoderBlock(256, 512) → skip1 (B, 512, H/8)      → MaxPool → (B, 512, H/16)
    ↓
bottleneck EncoderBlock(512, 1024) → (B, 1024, H/16)
    ↓
dec1 DecoderBlock(1024) + skip1 → cat(512+512=1024) → conv → (B, 512, H/8)
dec2 DecoderBlock(512)  + skip2 → cat(256+256=512)  → conv → (B, 256, H/4)
dec3 DecoderBlock(256)  + skip3 → cat(128+128=256)  → conv → (B, 128, H/2)
dec4 DecoderBlock(128)  + skip4 → cat(64+64=128)    → conv → (B, 64, H)
    ↓
output Conv2d(64, 1, kernel_size=1) → (B, 1, H, W)
```

## Key shape arithmetic at each concat

| Decoder level | Upsampled in | Skip in | After cat | After conv out |
|---|---|---|---|---|
| dec1 | (B, 512, H/8) | (B, 512, H/8) | (B, 1024, H/8) | (B, 512, H/8) |
| dec2 | (B, 256, H/4) | (B, 256, H/4) | (B, 512, H/4) | (B, 256, H/4) |
| dec3 | (B, 128, H/2) | (B, 128, H/2) | (B, 256, H/2) | (B, 128, H/2) |
| dec4 | (B, 64, H)   | (B, 64, H)   | (B, 128, H)   | (B, 64, H)   |

ConvTranspose2d(in_channels, in_channels//2) guarantees upsampled channels always equal skip channels — no skip_channels argument needed.

## Critical bugs caught during build

- Skip-decoder pairing reversed: skip1 (deepest, H/8) pairs with dec1 (first decoder after bottleneck), skip4 (shallowest, H) pairs with dec4. Reversed pairing causes spatial mismatch at every concat.
- Pool never called in forward: encoder blocks ran at full resolution, ConvTranspose2d then doubled an already full-size tensor.
- Bottleneck typo: EncoderBlock(516, 1024) should be EncoderBlock(512, 1024).
- Float division: in_channels/2 returns float; Conv2d requires int. Use // throughout.

## Reflection: why concat not add

UNet concatenates skip connections because encoder and decoder features at the same spatial level are in incompatible semantic spaces. Encoder features are spatially precise but semantically shallow — they know where things are. Decoder features are semantically rich but spatially coarse — they know what things are. Adding them would force the network to blend incompatible representations. Concatenation keeps both separate along the channel dimension and lets the following Conv2d learn how to combine them.

ResNet adds because both the shortcut and residual branch are in the same semantic space — addition is arithmetically and semantically coherent, and creates the gradient highway that lets the residual learn a correction on top of the identity.

Shape mismatch is NOT the reason for concat. At the concat point, spatial dimensions are identical by construction (ConvTranspose2d guarantees this).

## Spaced recall

Added to queue: "UNet concat vs ResNet add — semantic space incompatibility, not shape mismatch." Due: 2026-07-03.
