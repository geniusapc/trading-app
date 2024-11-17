from ib_insync import IB
# from config import IB_CLIENT_ID, IB_HOST,IB_PORT


IB_HOST = '127.0.0.1'
IB_PORT = 7497
IB_CLIENT_ID = 1
TARGET_PROFIT = 50

ib = IB()

async def connect_ib():
    await ib.connectAsync(IB_HOST, IB_PORT, clientId=IB_CLIENT_ID)
    return ib

async def disconnect_ib():
    if ib.isConnected():
        ib.disconnect()