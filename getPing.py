import speedtest
import datetime
import time
import matplotlib.pyplot as plt
import pandas as pd
from tkinter import *
from tkinter import font
from tkinter import filedialog
from tkinter.ttk import Progressbar


def runTest():
    if testLength.get() == "select test length":
        pass
    else:
        runButton.config(state=DISABLED)
        minutes = int(testLength.get())
        loopCount = getData(minutes)
        plotData(loopCount)


def plotData(loopCount):
    # read log
    df = pd.read_csv('ping_data.log',
                     names='date time ping download upload'.split(),
                     header=None,
                     sep=r'\s+',
                     parse_dates={'timestamp': [0, 1]},
                     na_values=['TEST', 'FAILED'])

    df_forPlot = df[-loopCount:]

    title = "getPing - " + str(datetime.date.today())

    # plot and save image file
    df_forPlot.plot(x="timestamp", y=["ping", "download", "upload"])
    plt.grid(color='grey', linestyle='-', linewidth=0.25, alpha=0.5)
    plt.title(title)
    plt.xlabel('time')
    plt.ylabel('mb/s')
    plt.savefig('apt7ping.png')

    progress['value'] = 100
    gp.update_idletasks()
    time.sleep(1)
    progress['value'] = 0
    gp.update_idletasks()

    testLength.set("complete")
    runButton.config(state="normal")
    graphButton.config(state="normal")
    doneButton.config(state="normal")


def getData(minutes):
    # clear log
    open('ping_data.log', 'w').close()

    duration = 60 * minutes
    timeEnd = time.time() + duration
    loopCount = 0

    # run test on loop for x minutes
    while time.time() < timeEnd:
        try:
            # initialize and run speed test
            servers = []
            threads = None

            s = speedtest.Speedtest()
            s.get_servers(servers)
            s.get_best_server()
            s.download(threads=threads)
            s.upload(threads=threads)
            s.results.share()
            results_dict = s.results.dict()

            # produce string element for each data point
            date = str(datetime.date.today())
            time_string = time.strftime("%H:%M:%S")
            download_raw = (results_dict["download"]) / 1000000
            download = str(round(download_raw, 2))
            upload_raw = (results_dict["upload"]) / 1000000
            upload = str(round(upload_raw, 2))
            ping = str(round(results_dict["ping"], 2))

            # append log file
            with open('ping_data.log', 'a') as f:
                print(date, time_string, ping, download, upload, file=f)

            loopCount += 1

            timeLeft = timeEnd - time.time()
            percent = 100 - round((timeLeft / duration) * 100)
            if percent < 100:
                progress['value'] = int(percent)
                gp.update_idletasks()
        except ValueError:
            pass
        else:
            pass
    return loopCount


def seeGraph():
    g = Toplevel()
    g.title("getPing")

    menuBar = Menu(g)
    fileMenu = Menu(menuBar, tearoff=0, bg="white", fg="black")
    fileMenu.add_command(label="Save graph as...", command=lambda: saveGraph())
    menuBar.add_cascade(label="File", menu=fileMenu)
    g.config(menu=menuBar)

    canvas = Canvas(g, height=480, width=640)
    canvas.grid(row=1, column=1)
    my_image = PhotoImage(file="apt7ping.png", master=gp)
    canvas.create_image(0, 0, anchor=NW, image=my_image)

    g.mainloop()


def exitDone():
    gp.destroy()
    exit()


OPTIONS = [2, 5, 10, 15, 30, 45, 60]

# Main GUI
gp = Tk()
gp.title("getPing")
gp.geometry("225x392")
gp.resizable(0, 0)
gp.configure(background='#00001a')

titleFont = font.Font(family="Helvetica", size=20, slant="italic")
buttonFont = font.Font(family="Helvetica", size=12, slant="italic")

testLength = StringVar()
testLength.set("select test length")

mainLabel = Label(gp, text="getPing", font=titleFont,
                  bg="#00001a", fg="white", width=15, height=4)
mainLabel.pack()

# drop down menu for selecting test length in minutes
lengthMenu = OptionMenu(gp, testLength, *OPTIONS)
lengthMenu.pack()

# Progress bar widget
progress = Progressbar(gp, orient=HORIZONTAL,
                       length=100, mode='determinate')
progress.pack(pady=10)

# buttons
runButton = Button(gp, text='run', command=lambda: runTest(), width=15, height=2,
                   font=buttonFont, bg="#33cccc", state="normal", fg="black")
runButton.pack()

graphButton = Button(gp, text='graph', command=lambda: seeGraph(), width=15, height=2,
                     font=buttonFont, state=DISABLED, bg="#ffc34d", fg="black")
graphButton.pack()
doneButton = Button(gp, text='done', command=lambda: exitDone(), width=15, height=2,
                    font=buttonFont, state=DISABLED, bg="#8f00b3", fg="black")
doneButton.pack()
gp.mainloop()
