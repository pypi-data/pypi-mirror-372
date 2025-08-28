# auditory_models

## Description

This repository provides multiple packages to compute auditory models, including
- Short term Objective Intelligibility ([STOI](https://ieeexplore.ieee.org/abstract/document/5713237))
- Generalized Power Spectrum Model for audio quality ([GPSMq](https://ieeexplore.ieee.org/abstract/document/8708700))


## Installation
`pip install auditory_models`

## Usage
```
from auditory_models import STOI, GPSMq
import soundfile as sf

reference, fs_ref = sf.read("reference.wav")
degraded, fs_dgr = sf.read("degraded.wav")
if fs_ref != fs_dgr:
    raise ValueError("Sample rates must be equal!")

stoi = STOI()
gpsmq = GPSMq(binaural=False)

stoi.process(reference, degraded, fs_ref)
gpsmq.process(reference, degraded, fs_ref)

```

## Support
Regarding issues please feel free to contact me via 
<a href="mailto:max.zimmermann@tugraz.at">max.zimmermann@tugraz.at</a>

## Contributing
Any contribution is welcome. 

## Authors and acknowledgment
Author: Max Zimmermann\
Credits to: 
- The developers of the original Matlab implementations
    - STOI: Cees Taal 
    - GPSMq: Thomas Biberger and Jan-Hendrik Fleßner
- Manuel Pariente for the original Python implementation of STOI

## License
This project is licensed under the GNU General Public License v3 (GPLv3). For further info see file `COPYING`.
