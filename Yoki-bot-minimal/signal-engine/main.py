from fastapi import FastAPI
app=FastAPI()
@app.get('/signal')
def sig(symbol:str='BANKNIFTY'):
    return {'signal':'watch','symbol':symbol}
