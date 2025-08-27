2Danalysis
==============================
[//]: # (Badges)

| **Latest release** | [![Last release tag][badge_release]][url_latest_release] ![GitHub commits since latest release (by date) for a branch][badge_commits_since]  [![Documentation Status][badge_docs]][url_docs]|
| :----------------- | :------- |
| **Status**         | [![GH Actions Status][badge_actions]][url_actions] [![codecov][badge_codecov]][url_codecov] |
| **Community**      | [![License: GPL v2][badge_license]][url_license]  [![Powered by MDAnalysis][badge_mda]][url_mda]|

[badge_actions]: https://github.com/monjegroup/twod-analysis-kit/actions/workflows/gh-ci.yaml/badge.svg
[badge_codecov]: https://codecov.io/gh/monjegroup/twod-analysis-kit/branch/main/graph/badge.svg
[badge_commits_since]: https://img.shields.io/github/commits-since/monjegroup/twod-analysis-kit/latest
[badge_docs]: https://readthedocs.org/projects/twod-analysis-kit/badge/?version=latest
[badge_license]: https://img.shields.io/badge/License-GPLv2-blue.svg
[badge_mda]: https://img.shields.io/badge/powered%20by-MDAnalysis-orange.svg?logoWidth=16&logo=data:image/x-icon;base64,AAABAAEAEBAAAAEAIAAoBAAAFgAAACgAAAAQAAAAIAAAAAEAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJD+XwCY/fEAkf3uAJf97wGT/a+HfHaoiIWE7n9/f+6Hh4fvgICAjwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACT/yYAlP//AJ///wCg//8JjvOchXly1oaGhv+Ghob/j4+P/39/f3IAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJH8aQCY/8wAkv2kfY+elJ6al/yVlZX7iIiI8H9/f7h/f38UAAAAAAAAAAAAAAAAAAAAAAAAAAB/f38egYF/noqAebF8gYaagnx3oFpUUtZpaWr/WFhY8zo6OmT///8BAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgICAn46Ojv+Hh4b/jouJ/4iGhfcAAADnAAAA/wAAAP8AAADIAAAAAwCj/zIAnf2VAJD/PAAAAAAAAAAAAAAAAICAgNGHh4f/gICA/4SEhP+Xl5f/AwMD/wAAAP8AAAD/AAAA/wAAAB8Aov9/ALr//wCS/Z0AAAAAAAAAAAAAAACBgYGOjo6O/4mJif+Pj4//iYmJ/wAAAOAAAAD+AAAA/wAAAP8AAABhAP7+FgCi/38Axf4fAAAAAAAAAAAAAAAAiIiID4GBgYKCgoKogoB+fYSEgZhgYGDZXl5e/m9vb/9ISEjpEBAQxw8AAFQAAAAAAAAANQAAADcAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAjo6Mb5iYmP+cnJz/jY2N95CQkO4pKSn/AAAA7gAAAP0AAAD7AAAAhgAAAAEAAAAAAAAAAACL/gsAkv2uAJX/QQAAAAB9fX3egoKC/4CAgP+NjY3/c3Nz+wAAAP8AAAD/AAAA/wAAAPUAAAAcAAAAAAAAAAAAnP4NAJL9rgCR/0YAAAAAfX19w4ODg/98fHz/i4uL/4qKivwAAAD/AAAA/wAAAP8AAAD1AAAAGwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALGxsVyqqqr/mpqa/6mpqf9KSUn/AAAA5QAAAPkAAAD5AAAAhQAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADkUFBSuZ2dn/3V1df8uLi7bAAAATgBGfyQAAAA2AAAAMwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAB0AAADoAAAA/wAAAP8AAAD/AAAAWgC3/2AAnv3eAJ/+dgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA9AAAA/wAAAP8AAAD/AAAA/wAKDzEAnP3WAKn//wCS/OgAf/8MAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIQAAANwAAADtAAAA7QAAAMAAABUMAJn9gwCe/e0Aj/2LAP//AQAAAAAAAAAA
[badge_release]: https://img.shields.io/github/release-pre/monjegroup/twod-analysis-kit.svg
[url_actions]: https://github.com/monjegroup/twod-analysis-kit/actions?query=branch%3Amain+workflow%3Agh-ci
[url_codecov]: https://codecov.io/gh/monjegroup/twod-analysis-kit/branch/main
[url_docs]: https://twodanalysis.readthedocs.io/en/latest/
[url_latest_release]: https://github.com/monjegroup/twod-analysis-kit/releases
[url_license]: https://www.gnu.org/licenses/gpl-2.0
[url_mda]: https://www.mdanalysis.org

Toolkit created to map biophysical properties of biopolymers (proteins, nucleic acids, glycans) onto surfaces, and those of lipid bilayers onto the membrane plane to track local and global changes in molecular dynamics and correlations in 2D. This kit is built following the format of MDAKits.

2Danalysis is bound by a [Code of Conduct](https://github.com/monjegroup/twod-analysis-kit/blob/main/CODE_OF_CONDUCT.md).

### Installation

To build `twodanalysis` from source,
We strongly recommend that you use virtual environments and
[Anaconda](https://docs.conda.io/en/latest/) as your package manager.
Below we provide instructions both for `conda` and `pip`.


#### With pip

First, create a virtual environment and activate it. You can do it with conda as follows:


```
conda create --name twod
conda activate twod
```

For easy installation, run:

```
pip install twod-analysis-kit
```

#### With conda

Ensure that you have [conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html) installed.

Create a virtual environment and activate it:

```
conda create --name twod
conda activate twod
```

Install the development and documentation dependencies:

```
git clone https://github.com/monjegroup/twod-analysis-kit.git
cd twod-analysis-kit
conda env update --name twod-analysis-kit --file devtools/conda-envs/test_env.yaml
conda env update --name twod-analysis-kit --file docs/requirements.yaml
```

Build this package from source:

```
pip install -e .
```

If you want to update your dependencies (which can be risky!), run:

```
conda update --all
```

And when you are finished, you can exit the virtual environment with:

```
conda deactivate
```


#### Tutorials!

The toolkit offers tutorials with a detailed explanation of the routines included in 2Danalysis, follow the tutorials step by step in this repo [pyF4all](https://github.com/pyF4all/2DanalysisTutorials) 

```
git clone https://github.com/pyF4all/2DanalysisTutorials.git
```

### Copyright

The 2D Analysis source code is hosted at https://github.com/monjegroup/twod-analysis-kit
and is available under the GNU General Public License, version 2 (see the file [LICENSE](https://github.com/monjegroup/twod-analysis-kit/blob/main/LICENSE)).

Copyright (c) 2025, Ricardo Ramirez, Antonio Bosch, Ruben Perez, Horacio V Guzman, and Viviana Monje


#### Acknowledgements
 
Project based on the 
[MDAnalysis Cookiecutter](https://github.com/MDAnalysis/cookiecutter-mda) version 0.1.
Please cite [MDAnalysis](https://github.com/MDAnalysis/mdanalysis#citation) when using 2D Analysis in published work.

#### Funding

H.V.G. acknowledges financial support from the Ramón y Cajal grant No. RYC2022-038082-I and Spanish Ministry of Science and Innovation, through project PID2023-150536NA-I00, and the “Severo Ochoa” Grant No. CEX2023-001263-S for Centers of Excellence; and thanks the Red Española de Supercomputación (RES) for the computing time and technical support at the Finisterrae III supercomputer project FI-2024-3-0033.

