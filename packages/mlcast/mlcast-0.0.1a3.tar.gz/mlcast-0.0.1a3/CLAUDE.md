This is the repo of the MLCast library, a machine learning (pytorch based) weather nowcasting and short-term forecasting library developed as a community effort by the Working Group 6 Nowcasting in the EUMETNET E-AI Optional Programme.
The library is in early stages (not usable atm) and we want shape it up to release the first version the will feature:
- code and pretrained models for 3 precipitation (radar) nowcasting models
- a first-class cli interface to use (generate forecats with the pretrained models), fintune and train the nowcasting models
- a clear and concise API 

Developement philosohpy and technical details:
- the dev environment is managed with `uv`
- LESS CODE is better than more
- the library is based on the pytorch + ligntning combo
    - the src/modules folder contains OLNY pure pytorch code (no lightning bits)
    - the src/models folder contains the abstract interfaces and the lightning parts
