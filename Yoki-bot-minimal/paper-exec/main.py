from fastapi import FastAPI
app=FastAPI()
@app.post('/exec')
def exe(order: dict):
    return {'status':'filled','order':order}
