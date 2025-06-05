# shakespeareChatBot

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
