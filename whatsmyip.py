#!/usr/bin/env python3
import select
import socket
import time

def available(conn):
	try:
		readable,writeable,errored=select.select([conn],[],[],0)
		if conn in readable:
			return True
	except Exception:
		pass
	return False

if __name__=='__main__':
	while True:
		try:
			sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
			sock.bind(('127.0.0.1',8082))
			sock.listen()

			while True:

				try:
					conn,addr=sock.accept()
					timeout=time.time()+2

					data=''
					response=''
					try:
						while len(data)==0 or available(conn):
							data+=conn.recv(4096).decode('utf-8')
							if time.time()>=timeout:
								response='HTTP/1.1 408 Request Timeout\r\nConnection: close\r\n\r\n'
								break
							if len(data)>1024*10:
								response='HTTP/1.1 413 Payload Too Large\r\nConnection: close\r\n\r\n'
								break
							if data.find('\r\n\r\n')>=0:
								data=data.split('\r\n\r\n')[0]
								break

						if len(response)==0:
							ip=addr[0]
							if ip=='127.0.0.1':
								for line in data.strip().split('\r\n'):
									key=line.split(':')
									val=':'.join(key[1:]).strip()
									key=key[0].strip()
									if key=='X-Real-IP' or key=='X-Forwarded-For':
										ip=val
										break
							response='HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nConnection: close\r\n\r\n'+ip+'\r\n'

					except Exception as error:
						response='HTTP/1.1 400 Bad Request\r\nConnection: close\r\n\r\n'
						#print(error)

					conn.send((response).encode('utf-8'))
					conn.close()

				except Exception as error:
					#print(error)
					pass

		except KeyboardInterrupt:
			exit(-1)

		except Exception as error:
			#print(error)
			time.sleep(1000)
