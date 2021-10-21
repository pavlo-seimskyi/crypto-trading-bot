import atexit
from apscheduler.schedulers.background import BackgroundScheduler

from flask import Flask, render_template

from credentials import BINANCE_API_KEY, BINANCE_API_SECRET
from src.order_executer.service.order_executer import OrderExecuter
from src.order_executer.service.portfolio import Portfolio

app = Flask(__name__)

my_portfolio = Portfolio(owner_name="Name", binance_key=BINANCE_API_KEY, binance_pass=BINANCE_API_SECRET)
executer_service = OrderExecuter(dev_run=False, portfolios=[my_portfolio])
scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(func=executer_service.step, trigger="interval", seconds=60)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())


@app.route("/trading/start", methods=["GET"])
def start():
    # Start the service. Initialize the necessary stuff
    try:
        if not executer_service.is_active:
            executer_service.start()
            return render_template('start.html')
        return render_template('start.html')
    except Exception as e:
        raise e


@app.route("/trading/close", methods=["GET"])
def close():
    # shutdown service and open positions. Don't shutdown until all positions are filled.
    executer_service.close()
    return render_template('start.html')

@app.route("/trading/restart", methods=["GET"])
def restart():
    # erase cache and restart service
    executer_service.close()
    executer_service.start()
    return render_template('restart.html')

@app.route("/trading/status", methods=["GET"])
def status():
    # return status of the service
    # time running
    # cache in features
    # trades done
    # profit won

    return


if __name__ == '__main__':
    app.run()


