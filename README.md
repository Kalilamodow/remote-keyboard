# remote keyboard

Client and server applications for sending keyboard events over network.

## how to use

Run `server.py` on whatever device you want to send keyboard events to, then run
`client.py` on the computer to send keyboard events from.

## drawbacks

- No pausing (you have to exit the client to be able to not
  send events)
- No security (literally anyone can just connect if they have the local
  ip)

## what is "socket_hlapi"

A thing I wrote a long time ago to make it easier to use two-way communication.
(At the time, I thought of it like native WebSockets)

## why does this exist

I didn't have a keyboard for my Raspberry Pi, so I wrote this. Now, I just
run the server in the background on my Pi, connect to it from my
desktop and connect my extra mouse to the Pi.
