# Polymer bonds in AlphaFold3
AlphaFold3
[does not allow](https://github.com/google-deepmind/alphafold3/blob/main/docs/input.md#bonds)
covalent bonds between/within polymer chains (protein, DNA, RNA).
We work around this limitation by treating one of the corresponding residue or nucleic acid as a modified residue/amino-acid.
In principle, this may enable AlphaFold3 to explicitly model e.g. disulfide bonds, cyclic peptides, zero-length crosslinkers, protein-DNA bonds..

*This is currently experimental/work-in-progress, please also have a look at complementary approaches
[KosinskiLab/af3x](https://github.com/KosinskiLab/af3x)
and
[bio-phys/polyUb-AF](https://github.com/bio-phys/polyUb-AF).*

## Quick start
```bash
git clone git@github.com:jurgjn/alphafold3-polymer-bonds.git
cd alphafold3-polymer-bonds
pip install -e .
```