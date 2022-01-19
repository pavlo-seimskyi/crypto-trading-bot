import atexit

from apscheduler.schedulers.background import BackgroundScheduler

from flask import Flask, render_template, redirect, url_for, request

from credentials import BINANCE_API_KEY, BINANCE_API_SECRET
from src.data_scraper.scraper_binance import BinanceScraper
from src.order_executer.service.data_service import ProductionDataService
from src.order_executer.ui import active_screen
from src.order_executer.service.order_executer import OrderExecuter
from src.order_executer.service.portfolio import Portfolio

app = Flask(__name__)

my_portfolio = Portfolio(owner_name="Name", api_key=BINANCE_API_KEY, api_secret=BINANCE_API_SECRET)
data_service = ProductionDataService(interval_period_in_minutes=1, channels=[BinanceScraper()])
executer_service = OrderExecuter(data_service=data_service, portfolios=[my_portfolio])

scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(func=executer_service.step, trigger="interval", seconds=60)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())


@app.route("/", methods=["GET", "POST"])
def home():
    # Start the service. Initialize the necessary stuff
    if request.method == "POST":
        if request.form.get('action') == 'START':
            return redirect(url_for('start'))

    return render_template('home.html')


@app.route("/start", methods=["GET", "POST"])
def start():
    try:
        if not executer_service.is_active:
            executer_service.start()
            return redirect(url_for('active'))
        return redirect(url_for('active'))
    except Exception as e:
        raise e


@app.route("/active", methods=["GET", "POST"])
def active():
    # Show plot
    if request.method == "POST":
        if request.form.get('action') == 'CLOSE':
            return redirect(url_for('close'))
        elif request.form.get('action') == 'REFRESH':
            return redirect(request.referrer)
        elif request.form.get('action') == 'RESTART':
            return redirect(url_for('restart'))

    return show_graph()


@app.route("/close", methods=["GET", "POST"])
def close():
    # shutdown service and open positions. Don't shutdown until all positions are filled.
    executer_service.close()
    return render_template('close.html')


@app.route("/restart", methods=["GET", "POST"])
def restart():
    # erase cache and restart service
    executer_service.close()
    executer_service.start()
    return redirect(url_for('active'))


def show_graph():
    graphJSON = active_screen.plot_metrics(executer_service)
    return render_template('active.html', graphJSON=graphJSON)


if __name__ == '__main__':
    app.run()
