import socket
import time
import datetime
import sys
import os
import utils
import Queue

from Parser import Parser
from ScrolledText import ScrolledText
from Tkinter import *
from threading import *
from socket import *


inputQueue = Queue.Queue()
buildQueue = Queue.Queue()

class Recieve():
    def __init__(self, client):
        #self.messageHistory = messageHistory
        while True:
            try:
                text = client.recv(1024)
                if not text:
                    break
                else:
                    if text.startswith("8"):
                        prs = Parser()
                        self.text = text
                        #self.sframe = Frame(frame)
                        #self.sframe.pack(anchor='w')
                        #print text
                        prs.breakdown(text)
                        inputQueue.put(self.text)
                        time.sleep(2)
                        #self.messageHistory = ScrolledText(root, undo = True)
                        #self.messageHistory.bind("<Key>", lambda e: "break")
                        #self.messageHistory.pack()
                        #self.messageHistory.insert(END,"Welcome " + prs.alias +" to the " + prs.room + " chat room!")
                        #inputQueue.put(self.text)
                    if text.startswith("5"):
                        print text
                        buildQueue.put(text)
                        #self.messageHistory.insert(END, text)
                    #print text
                    else:
                        #print text
                        inputQueue.put(text)
                    #print inputQueue.get()
            except:
                break


class App(Thread):

    alias = None
    room = None
    flag = False
    client = socket()
    IP = raw_input("IP Address: " )
    if not IP:
        IP = 'localhost'
    try:
        client.connect((IP, 9000))
    except:
        print "Could not connect to IP"
        exit()

    def __init__(self, master):
        Thread.__init__(self)
        frame = Frame(master)
        frame.pack()
        #self.messageHistory = ScrolledText(frame, undo = True)
        #self.messageHistory.bind("<Key>", lambda e: "break")
        #self.messageHistory.pack()
        #self.sframe = Frame(frame)
        #self.sframe.pack(anchor='w')

        self.setAlias()

    def run(self):

        Recieve(self.client)

    def clearWindow(self):
        for widget in root.winfo_children():
                widget.destroy()

    def assemble_packet(self, msg, code):
        parser = Parser()
        if code == utils.codes["send_msg"]:
            date = datetime.datetime.now().strftime(utils.DATE_FORMAT)
            print self.alias
            print self.room
            print date
            print msg
            packet = parser.assemble(utils.codes["send_msg"],self.alias,self.room,date,msg)
        elif code == utils.codes["set_alias"]:
            packet = parser.assemble(utils.codes["set_alias"],msg,"","","")
        elif code == utils.codes["set_room"]:
            packet = parser.assemble(utils.codes["set_room"],self.alias,msg,"","")
        elif code == utils.codes["get_roomlist"]:
            packet = parser.assemble(utils.codes["get_roomlist"],self.alias,"","","")
        print("Sending packet %s" %(packet))
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
            print("Invalid packet recieved")
            return

    def setAlias(self):

        def setRoom():
            aliasCheck = None
            self.alias = self.aliasInfo.get().translate(None, '\\')
            packet = self.assemble_packet(self.alias, utils.codes["set_alias"])
            self.client.send(packet)
            time.sleep(1)
            if not inputQueue.empty():
                aliasCheck = str(inputQueue.get())
                #This code is ruffff
                if aliasCheck.startswith("7"):
                    roomList = self.breakdown_packet(aliasCheck)
                    self.clearWindow()
                    self.changeRoom(roomList)
            else:
                self.flag = True
                self.clearWindow()
                self.setAlias()


        self.intro = Label(root, text = "Everyone Else Is Trash", width=600, font=8000, fg="red", pady = 100)
        self.intro.pack(anchor = CENTER)
        self.aliasLabel = Label(root, text = "Set Your Alias:", pady = 10)
        self.aliasLabel.pack(anchor = CENTER)
        self.aliasInfo = Entry(root, width = 40)
        self.aliasInfo.pack(anchor = CENTER)
        self.spacing = Label(root, text = "", pady = 70)
        if self.flag == True:
            self.spacing.config(text = "Alias name is already taken")
            self.flag = False
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
            self.client.send(packet)
            time.sleep(1)
            if not inputQueue.empty():
                roomCheck = str(inputQueue.get())
                #print roomCheck
                if roomCheck.startswith("8"):
                    self.room = chosenRoom
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
                packet = self.assemble_packet(message, utils.codes["send_msg"])
                self.client.send(packet)

                '''endOfBox=self.messageHistory.vbar.get()
                self.messageHistory.insert(END, "\n" + message)
                if endOfBox[1]==1.0:
                    endOfBox=self.messageHistory.see("end")'''

        def changingRoom():
            self.clearWindow()
            self.changeRoom()

        root.title("TrashTalk - " + room)
        self.messageHistory = ScrolledText(root, undo = True)
        self.messageHistory.bind("<Key>", lambda e: "break")
        self.messageHistory.pack(anchor=W)
        self.messageHistory.insert(END,"Welcome " + self.alias +" to the " + room + " chat room!")
        self.entryBox = Entry(root, width = 85)
        self.entryBox.place(x = 0, y = 392, anchor=W)
        self.sendButton = Button(root, height=2, width=19, text = "Send Message", command = newMessage)
        self.sendButton.place(x = 518, y = 388, anchor = NW)
        self.sendButton = Button(root, height=2, width=19, text = "Change Room", command = changingRoom)
        self.sendButton.place(x = 725, y = 300, anchor = NW)


        def polling():
            if not buildQueue.empty():
                MYINFO = buildQueue.get()
                
                self.messageHistory.insert(END, "\n" + MYINFO)
            root.after(500, polling)

        root.after(500, polling)



if __name__ == "__main__":

    root = Tk()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    root.iconbitmap(r''+dir_path+'/py.ico')
    root.resizable(width=False, height=False)
    root.title('TrashTalk')
    root.geometry('{}x{}'.format(960, 540))
    app = App(root).start()

    root.mainloop()