# Grussauftraege-KFR
This data collection consists of letters from the period around 1800, primarily those of August Wilhelm Schlegel, Friedrich Schlegel, Dorothea Veit-Schlegel, Caroline Schlegel-Schelling, and their correspondents. The data is structured in such a way as to facilitate analysis of social networks and communication patterns between historical personalities. Greeting orders, i.e. requests to an intermediary to greet one or more third parties, are a frequent feature of these letters, and the project aims to analyse these requests in order to understand the social dynamics of the time and to identify patterns that suggest the functions of greetings and greeting orders, as explained in the article *Grüßen – grüßen lassen*.


### Sample network: Network of Illocution *grüßen lassen* - August Wilhelm, Friedrich, Dorothea und Caroline Schlegels
<img width="3436" height="3778" alt="Image" src="https://github.com/user-attachments/assets/33ed188a-a67a-4659-903b-b66cb3632135" />

# Data
The source data comes from the collection of letters from the *Correspondence of Early Romanticism* project (https://briefe-der-romantik.de/), which builds on the *Digital Edition of August Wilhelm Schlegel's Correspondence* project (https://august-wilhelm-schlegel.de/briefedigital/). The annotation practice there was extended to include the labelling of statements in the letter in triple or quadruple structures. The data was processed in order to extract relevant information for the network analysis. The data is organized into the following directories:
- `network_degree`: Contains CSV files with network degree data, which includes information about the connections between individuals in the letters.
- `network_diagram`: Contains PNG files with visual representations of the networks derived from the letters

# Literature
- August Wilhelm Schlegel: Digitale Edition der Korrespondenz. Hg. von Jochen Strobel und Claudia Bamberg. Dresden, Marburg, Trier 2014–2020; https://august-wilhelm-schlegel.de.
- Korrespondenzen der Frühromantik; https://briefe-der-romantik.de/

# Citation
If you use this project in your research, please cite it as follows:
```
Fath, Laura & Strobel, Jochen unter Mitwirkung von Gwanghun Park (2025). Grüßen – und grüßen lassen. In Aline Deicke, Jochen Strobel (Hg.), Connecting the Dots. Briefe in Literaturwissenschaft und Digital Humanities. De Gruyter. (preprint)
```

# Directory structure
```
├── network_degree: CSV files containing network degree data. Delimited by semicolons.
├── network_diagram: PNG files containing network diagrams.
├── src
│   └── Grussauftraege-KFR
│       └── tools: Main functions for Jupyter notebooks.
│           └── __init__.py
│           └── network.py: Network analysis functions for the package.
│       └── __init__.py
│       └── network_analysis_gruessen_lassen.ipynb: Network analysis of illocution grüßen lassen.
│       └── network_analysis_gruessen.ipynb: Network analysis of illocution grüßen.
│       └── network_analysis_gruessen_schlegel.ipynb: Network analysis of August Wilhelm Schlegels correspondence.
├── .gitignore: gitignore file.
├── LICENSE.md: Project license file.
├── poetry.lock: Poetry lock file.
├── pyproject.toml: Poetry configuration file.
└── README.md: This file.
```

# License
This project is licensed under the CC-BY-SA-4.0 license. See the [LICENSE.md](LICENSE.md) file for details.