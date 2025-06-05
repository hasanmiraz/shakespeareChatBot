# shakespeareChatBot
An Expert on shakespeare literature. it uses a quantised model with RAG to generate the most accurate result of your query. <br>

**A breakdown of the Bot** <br>
**Embedder:** ```sentence-transformers/all-mpnet-base-v2``` <br>
**Model:** ```Qwen/Qwen2.5-7B-Instruct``` <br>
**Dataset:** ```https://www.kaggle.com/datasets/kingburrito666/shakespeare-plays``` <br>
**Dataconversion Repo:** ```https://github.com/tabifonica/shakespeare-data-prep``` <br>

Other stuff: <br>
**Frontend:** ```ReactJS``` <br>
**Backend:** ```FastAPI``` <br>

***BIG GPU IS REQUIRED***

## BE and AI setup
create an env:
```
python -m venv venv
```
install the requirements:
```
pip install -r 'requirements.txt'
```

### BE host
get into BE directory:
```
cd shakespeareChatBot
```
host BE:
```
uvicorn shakespeareChatBotBE.main:app --reload
```

## FE setup
get into the FE directory:
```
cd shakespeareChatBotFE
```
install dependencies:
```
npm install
```

### FE host
```
npm run dev
```
