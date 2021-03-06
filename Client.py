import socket
import time
import datetime
import sys
import os
import utils
import Queue
import logging

from Parser import Parser
from ScrolledText import ScrolledText
from Tkinter import *
from threading import *
from socket import *


inputQueue = Queue.Queue()  #stores command packets
buildQueue = Queue.Queue() #stores message packets

#this class runs on its own thread and listens for packets that it recieves from the server
class Recieve():
    def __init__(self, client):
        self.listen(client)

    def listen(self,client):
        while True:
            try:
                text = client.recv(utils.BUFF_SIZE)
                logging.info("Recieved packet: %s" % (text))
                if text:
                    parser = Parser()
                    parser.breakdown(text)
                    if parser.code == utils.codes["recv_msg"] or parser.code == utils.codes["leave_room"]:
                        buildQueue.put(text)
                    elif parser.code == utils.codes["quit_client"]:
                        client.close()
                        os._exit(1)
                    else:
                        inputQueue.put(text)
                else:
                    raise Exception
            except Exception as e:
                logging.exception(e)
                break

#this thread creates the buttons in the GUI and listens for any change in them
class client_GUI(Thread):

    alias = None
    room = None
    flag = False
    in_room = False
    client = socket()
    IP = raw_input("IP Address: " )
    if not IP:
        IP = 'localhost'
    try:
        client.connect((IP, 9000))
    except Exception as e:
        print "Could not connect to IP"
        logging.exception(e)
        exit()

    def __init__(self, master):
        Thread.__init__(self)
        frame = Frame(master)
        frame.pack()
        self.setAlias()

    #creates the thread for listening to the Server
    def run(self):
        Recieve(self.client)

    def clearWindow(self):
        for widget in root.winfo_children():
                widget.destroy()

    def assemble_packet(self, msg, code):
        parser = Parser()
        if code == utils.codes["send_msg"]:
            date = datetime.datetime.now().strftime(utils.DATE_FORMAT)
            packet = parser.assemble(utils.codes["send_msg"],self.alias,self.room,date,msg)
        elif code == utils.codes["set_alias"]:
            packet = parser.assemble(utils.codes["set_alias"],msg,"","","")
        elif code == utils.codes["set_room"]:
            packet = parser.assemble(utils.codes["set_room"],self.alias,msg,"","")
        elif code == utils.codes["get_roomlist"]:
            packet = parser.assemble(utils.codes["get_roomlist"],self.alias,self.room,"","")
        logging.info("Sending packet %s" %(packet))
        return packet

    def breakdown_packet(self,packet):
        parser = Parser()
        parser.breakdown(packet)
        if parser.code == utils.codes["recv_msg"]:
            return parser.body
        elif parser.code == utils.codes["recv_roomlist"]:
            return parser.body
        elif parser.code == utils.codes["alias_success"]:
            self.alias = parser.alias
            return parser.body
        elif parser.code == utils.codes["alias_invalid"]:
            return parser.alias
        elif parser.code == utils.codes["room_success"]:
            self.room = parser.room
            return parser.room
        elif parser.code == utils.codes["room_invalid"]:
            return parser.room
        else:
            logging.info("Invalid packet recieved")
            return

    def setAlias(self):

        def setRoom():
            aliasCheck = None
            self.alias = self.aliasInfo.get().translate(None, '\\')
            self.alias = self.alias.translate(None, ' ')
            if len(self.alias) > 20:
                self.alias = self.alias[:19]
            packet = self.assemble_packet(self.alias, utils.codes["set_alias"])
            try:
                self.client.send(packet)
            except Exception as e:
                logging.exception(e)
            time.sleep(1)
            if not inputQueue.empty():
                aliasCheck = str(inputQueue.get())
                if aliasCheck.startswith(utils.codes["alias_success"]):
                    roomList = self.breakdown_packet(aliasCheck)
                    self.clearWindow()
                    self.changeRoom(roomList)
                else:
                    self.flag = True
                    self.clearWindow()
                    self.setAlias()
            else:
                self.flag = True
                self.clearWindow()
                self.setAlias()

        self.intro = Label(root, text = "Welcome to TrashTalk", width=600, font=8000, fg="red", pady = 100)
        self.intro.pack(anchor = CENTER)
        self.aliasLabel = Label(root, text = "Set Your Alias:", pady = 10)
        self.aliasLabel.pack(anchor = CENTER)
        self.aliasInfo = Entry(root, width = 40)
        self.aliasInfo.pack(anchor = CENTER)
        self.spacing = Label(root, text = "", pady = 70)
        if self.flag:
            self.spacing.config(text = "Invalid, please try again", fg = "red")
        self.spacing.pack(anchor = CENTER)
        self.login = Button(root, height=2, width=10, text = "Pick A Room", command = setRoom)
        self.login.pack(anchor = CENTER)

    def changeRoom(self, roomList):

        def enterRoom():
            self.clearWindow()
            chosenRoom = self.v.get()
            if not chosenRoom:
                chosenRoom = firstRoom
            packet = self.assemble_packet(chosenRoom, utils.codes["set_room"])
            try:
                self.client.send(packet)
            except Exception as e:
                logging.exception(e)
            time.sleep(1)
            if not inputQueue.empty():
                roomCheck = str(inputQueue.get())
                if roomCheck.startswith(utils.codes["room_success"]):
                    self.room = chosenRoom
                    self.in_room = True
                    self.inRoom(chosenRoom)
            else:
                self.changeRoom(roomList)

        root.title("TrashTalk")
        rooms = roomList.split()
        firstRoom = rooms[0]
        self.v = StringVar(value=firstRoom)
        self.roomLabel = Label(root, text = "Select which Chat Room You Would Like to Join", pady = 70, font = 800)
        self.roomLabel.pack(anchor=CENTER)
        for room in rooms:
            self.b = Radiobutton(root, text = room, variable = self.v, value = room)
            self.b.pack(anchor=CENTER)
        self.b.deselect()
        self.login = Button(root, height=2, width=20, text = "Enter Chosen Room", command = enterRoom)
        self.login.place(relx=0.5, y=400, anchor = CENTER)


    def inRoom(self, room):

        def newMessage():
            message = self.entryBox.get()
            if message:
                self.entryBox.delete(0, 'end')
                message = message.translate(None, '\\')
                if len(message) > 900:
                    message = message[:899]
                packet = self.assemble_packet(message, utils.codes["send_msg"])
                try:
                    self.client.send(packet)
                except Exception as e:
                    logging.exception(e)

        def changingRoom():
            packet = self.assemble_packet("", utils.codes["get_roomlist"])
            try:
                self.client.send(packet)
            except Exception as e:
                logging.exception(e)
            time.sleep(1)
            if not inputQueue.empty():
                roomCheck = str(inputQueue.get())
                if roomCheck.startswith(utils.codes["recv_roomlist"]):
                    in_room = False
                    roomList = self.breakdown_packet(roomCheck)
                    self.clearWindow()
                    self.changeRoom(roomList)

        def exitProgram():
            self.client.close()
            os._exit(1)

        root.title("TrashTalk - " + room)
        self.messageHistory = ScrolledText(root, undo = True)
        self.messageHistory.bind("<Key>", lambda e: "break")
        self.messageHistory.pack(anchor=W)
        self.messageHistory.insert(END,"Welcome " + self.alias +" to the " + room + " chat room!")
        self.entryBox = Entry(root, width = 85)
        self.entryBox.place(x = 0, y = 400, anchor=W)
        self.sendButton = Button(root, height=2, width=19, text = "Send Message", command = newMessage)
        self.sendButton.place(x = 518, y = 388, anchor = NW)
        self.sendButton = Button(root, height=4, width=25, text = "Change Room", command = changingRoom)
        self.sendButton.place(x = 725, y = 300, anchor = NW)
        self.sendButton = Button(root, height=4, width=25, text = "Quit", command = exitProgram)
        self.sendButton.place(x = 725, y = 400, anchor = NW)

        def update_chat():
            if not buildQueue.empty():
                MYINFO = buildQueue.get()
                if MYINFO.startswith(utils.codes["leave_room"]):
                    changingRoom()
                elif self.in_room:
                    msg = self.breakdown_packet(MYINFO)
                    endOfBox=self.messageHistory.vbar.get()
                    self.messageHistory.insert(END, "\n" + msg)
                    if endOfBox[1]==1.0:
                        endOfBox=self.messageHistory.see("end")
            root.after(100, update_chat)

        root.after(100, update_chat)

if __name__ == "__main__":
    logging.basicConfig(filename='Clientlog.log', format='%(asctime)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S%p\t', level=logging.DEBUG)
    root = Tk()

    #sets the favicon of the GUI to our own custom icon
    dir_path = os.path.dirname(os.path.realpath(__file__))
    root.iconbitmap(r''+dir_path+'/py.ico')

    root.resizable(width=False, height=False)
    root.title('TrashTalk')
    root.geometry('{}x{}'.format(960, 540))
    GUI_thread = client_GUI(root).start() #starts the thread that runs our GUI

    root.mainloop()
