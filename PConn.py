import threading, time, signal,logging, sys
from gi.repository import  Gio, GLib
class tcon():
	def __init__(self,q,ip,c,v):
		self.receiver_ip = ip
		self.commport= c
		self.vcommport=v
		self.q=q
		self.sock = None
		self.vsock = None

		self.connection = None
		self.cconnection = None
		self.socket = None
		self.csocket = None
		self.csocket1 = None
		self.transport = None
		self.ctransport = None
		self.dtransport = None
		#self.internet_connection()
		#self.q.put_nowait("receiver_ip=103.237.39.107:4000")
	def sock_events3(self, socket_client, event, connectable, connection):

		print str(event)+" event for :3000"
		if event == Gio.SocketClientEvent.CONNECTED:
			self.cconnection1 = connection
		if event == Gio.SocketClientEvent.COMPLETE and connection is not None:

			self.cconnection1 = connection
			if connection.is_connected():
				self.csocket1 = connection.get_socket()
				self.csocket1.set_keepalive(True)
				print str(self.csocket1.get_keepalive())

				self.csocket1.set_blocking(False)
				print str(self.csocket1.get_blocking())

				self.in_connection1 = connection.get_input_stream()
				self.dtransport = connection.get_output_stream()
				
		print str(connection)
	def sock_events2(self, socket_client, event, connectable, connection):
		print str(event)+" event for :"+str(self.vcommport)
		if event == Gio.SocketClientEvent.CONNECTED:
			self.cconnection = connection
		if event == Gio.SocketClientEvent.COMPLETE and connection is not None:
			self.cconnection = connection
			if connection.is_connected():
				self.csocket = connection.get_socket()
				self.csocket.set_keepalive(True)
				print str(self.csocket.get_keepalive())
				self.csocket.set_blocking(False)
				print str(self.socket.get_blocking())
				self.q.put_nowait("connected")
				self.in_connection = self.cconnection.get_input_stream()
				self.ctransport = self.cconnection.get_output_stream()
		print str(connection)

	def sock_events(self, socket_client, event, connectable, connection):
		print str(event) + " event for :" + str(self.commport)
		if event == Gio.SocketClientEvent.CONNECTED:
			self.connection = connection
		if event == Gio.SocketClientEvent.COMPLETE and connection is not None:
			self.connection = connection
			if connection.is_connected():
				self.socket = connection.get_socket()
				self.socket.set_keepalive(True)
				print str(self.socket.get_keepalive())
				self.socket.set_blocking(False)
				print str(self.socket.get_blocking())
				inp = connection.get_input_stream()
				self.transport = connection.get_output_stream()
				th1 = threading.Thread(target=self.myreader, args=(inp,))
				th1.start()
				self.q.put_nowait("connected")
	def internet_connection(self):
		while self.receiver_ip is None:
			fetcherror = False
			logging.debug("Checking Internet connection")
			client = Gio.SocketClient()
			client.set_timeout(5)
			#socket = Gio.InetSocketAddress("108.161.136.107", 3000)
			conn_error = False
			try:
				conn = client.connect_to_uri("http://108.161.136.107:3000/getinfo",  3000)
			except:
				conn_error=True
				#GLib.timeout_add_seconds(1, self.internet_connection)
			if conn_error == False:
				try:
					outp = conn.get_output_stream()
					message = "GET /getinfo HTTP/1.1\r\nHost: 108.161.136.107:3000\r\n\r\n"
					outp.write(message)
					inp = conn.get_input_stream()
					data = inp.read_bytes(8192, Gio.Cancellable.new()).get_data().split('\r\n')
					line = data[len(data) - 1]
					if line.find(":") > 0:
						rd = line.split(':')
						if(len(rd)==3):
							logging.debug(line)
							self.receiver_ip = rd[0].strip()
							self.commport = int(rd[1])
							self.vport = int(rd[2])
							self.q.put_nowait("receiver_ip="+self.receiver_ip+":"+rd[2].strip())
							logging.debug("receiver_ip=" + self.receiver_ip + ":" + str(self.vport) + " :" + str(self.commport))
							conn.close(None)
				except Exception:
					logging.debug("Exception found after making connection")
		#self.start()

	def myreader(self,inp):
		logging.debug("Socket reader has been started")
		while self.connection is not None:
			try:
				data=inp.read_bytes(8192, Gio.Cancellable.new()).get_data()
			except Exception:
				data=''
			if data:
				datas=data.split('\n')
				for d in datas:
					if d!='':
						self.q.put_nowait(d)
						logging.debug(d)
			else:
				self.q.put_nowait("disconnected")
				#self.connection.close(None)
				#self.cconnection.close(None)
				self.socket.close()
				self.csocket.close()
				exit()
		#self.start()
		"""
			def send(self,data):
		try:
			self.transport.write(str(data)+'\n')
			#logging.debug("Sent tp server:" + data)
		except Exception:
			logging.debug("Failed to send data" + str(data))
			if data == 'vinfo' or data == 'playnow' or data == 'end':
				result = False
				while result == False:
					time.sleep(.1)
					try:
						self.transport.write(data)
						result = True
					except Exception:
						result = False
		"""

	def cwatch(self,channel, cond, *data):
		if cond == GLib.IOCondition.IN:
			inp = self.connection.get_input_stream()
			th1 = threading.Thread(target=self.myreader, args=(inp,))
			th1.start()
		elif cond == GLib.IOCondition.OUT:
			self.q.put_nowait("connected")
	def send(self,data):
		data=str(data)+'\n'
		if self.socket.is_connected():
			check=self.socket.condition_check(GLib.IOCondition.OUT)
			if check == GLib.IOCondition.OUT:
				try:
					i = self.transport.write_all(data)
					self.transport.flush()
				except Exception:
					self.q.put_nowait("disconnected")
					self.socket.close()
					self.csocket.close()

	def sendgst(self,data,rf):
		self.stopper = 0
		if self.csocket.is_connected():
			check=self.csocket.condition_check(GLib.IOCondition.OUT)
			if check == GLib.IOCondition.OUT:
				try:
					i = self.ctransport.write_all(data)
					self.ctransport.flush()
					logging.debug("gst="+str(sys.getsizeof(data)))
				except Exception:
					self.q.put_nowait("disconnected")
					self.socket.close()
					self.csocket.close()



	def sendgst1(self,data):
		self.stopper = 0
		if self.csocket1.is_connected():
			check=self.csocket1.condition_check(GLib.IOCondition.OUT)
			if check == GLib.IOCondition.OUT:
				i = self.dtransport.write_all(data)
				self.ctransport.flush()
				logging.debug("gst1="+str(i))

	def start(self):
		addr = Gio.InetSocketAddress.new_from_string(self.receiver_ip, self.commport)
		addr2 = Gio.InetSocketAddress.new_from_string(self.receiver_ip, self.vcommport)

		self.sock = Gio.SocketClient.new()
		self.csock = Gio.SocketClient.new()

		self.sock.connect_data("event", self.sock_events)
		self.csock.connect_data("event", self.sock_events2)


		try:
			self.sock.connect(addr, Gio.Cancellable.new())

		except GLib.Error:

			print "GLIB ERROR for connecting:"+str(self.commport)
			time.sleep(2)
			self.start()
		try:
			self.csock.connect(addr2, Gio.Cancellable.new())
		except GLib.Error:
			print "GLIB ERROR for connecting:"+str(self.vcommport)
			time.sleep(2)
			self.start()
