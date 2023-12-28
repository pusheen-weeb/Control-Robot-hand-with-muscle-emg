import time
import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation

def nhan_data_plot():
    arduinoData = serial.Serial('com3', 115200)
    time.sleep(1)

    cb1_values = []
    cb2_values = []

    fig, ax = plt.subplots()

    def update_plot(frame):
        while arduinoData.inWaiting() > 0:
            dataPacket = arduinoData.readline()
            dataPacket = str(dataPacket, 'utf-8')
            dataPacket = dataPacket.strip('\r\n')
            splitPacket = dataPacket.split(",")

            cb1 = float(splitPacket[0])
            cb2 = float(splitPacket[1])
            dc1 = float(splitPacket[2])
            dc2 = float(splitPacket[3])

            print("cb1 = ", cb1, " cb2 = ", cb2, " dc1 = ", dc1, " dc2 = ", dc2)

            cb1_values.append(cb1)
            cb2_values.append(cb2)

            ax.clear()
            ax.plot(cb1_values, label = 'cb1')
            ax.plot(cb2_values, label = 'cb2')
            ax.legend()

            plt.pause(0.001)

    ani = animation.FuncAnimation(fig, update_plot, interval = 100)

    plt.show()
        
nhan_data_plot()
