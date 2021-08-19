from src.order_executer.service.order_executer import OrderExecuter

executer_service = OrderExecuter(dev_run=True)

while True:
    executer_service.step()