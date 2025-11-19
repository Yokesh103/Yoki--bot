from fastapi import FastAPI
app=FastAPI()
@app.get('/optionchain')
def get_chain(symbol: str='BANKNIFTY'):
    return {'symbol':symbol,'data':'placeholder'}
