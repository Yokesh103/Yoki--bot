from fastapi import FastAPI
app=FastAPI()
@app.post('/submit')
def sub(order: dict):
    return {'accepted':True,'order':order}
