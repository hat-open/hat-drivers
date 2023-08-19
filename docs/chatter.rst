.. _hat-drivers-chatter:

`hat.drivers.chatter` - Chatter communication protocol
======================================================

Hat defines a communication infrastructure used by Hat back-end components.
This communication is based on the TCP communication protocol (with the option
of applying an SSL layer on top of TCP) and messages encoded using SBS. The
underlying stream is segmented into blocks. Each block contains a single
communication message prefixed by its message header. This header consists of
`1+m` bytes where the first byte contains the value `m` (from 0 to 255, or
header byte length), while the `m` bytes value determines the number of
following message bytes (`k`) encoded as big-endian (the first byte value does
not include the first header byte and message length does not include header
length) which contain the actual body of the message.

Visualization of the communication stream::

    address    ...  |  n  | n+1 |  ...  | n+m | n+m+1 |  ...  | n+m+k |  ...
             -------+-----+-----+-------+-----+-------+-------+-------+-------
       data    ...  |  m  |         k         |        message        |  ...
             -------+-----+-----+-------+-----+-------+-------+-------+-------

where:

    * `m` is byte length of `k`
    * `k` is byte length of `message` (`n+1` is the most significant byte)
    * `message` is SBS encoded message data.

All Communication is peer-to-peer based. One peer connects to another and once
the connection is achieved, each peer can send messages to the other peer in
full duplex fashion. Each peer can terminate the connection if necessary. Most
communication errors (including data serialization errors) will result in
connection termination.


Message
-------

Communication message is defined by SBS `HatChatter.Msg` containing:

* unique message identifier (`id`)
* conversation descriptor (`first`, `owner`, `token`, `last`)
* message data (`data`) determined by type identifier ('type')

Message identifier is a number which uniquely identifies a peer's message. When
a new connection is established, each peer bounds a counter to the connection.
Upon sending a new message, this counter is incremented and used as the new
message's identifier.

Conversation descriptor consists of a set of parameters which bind the message
to a specific conversation (see Conversation_).

Message data consists of bytes with additional type identifier. Usually type
represents SBS type identifier and data contains SBS encoded data
(this kind of data encoding is not mandated by Chatter). Type identifiers
starting with ``HatChatter.`` are reserved for Chatter internal encoding and
should not be used.

SBS message schema:

.. include:: ../schemas_sbs/chatter.sbs
   :literal:


Conversation
------------

A Conversation is defined as an ordered finite sequence of messages.
Conversations are used for short ordered exchange of messages between two
peers. Each peer can start a new conversation and finalize an existing
conversation. Multiple simultaneously active conversations can be bound to
a single active connection. A basic example for conversation usage is a
request-response message exchange between peers, implementing operation
timeouts.

Each message contains its conversation descriptor which contains:

* conversation's first message identifier (`first`)
* owner flag (`owner`)
* token passing flag (`token`)
* last message flag (`last`)

A Conversation's first message identifier contains the message identifier of
the message which started the conversation. If this identifier is equal to
the current message's identifier, the message is the first message in
the conversation.

The peer who initiates a conversation (sends the first message in the
conversation) is considered to be the conversation's owner. A message's
owner flag (`owner`) is set to ``true`` only if the peer sending the message is
also the conversation's owner.

The token passing flag (`token`) is set to ``true`` if this message is the last
message this peer will send prior to expecting messages (bound to the current
conversation) from the other peer. This behavior is an implementation of the
token passing mechanism. Initially, the token is given to the peer who
initiates the conversation. This peer can pass the token to the other peer by
setting the token passing flag (`token`) to ``true``. Only the peer currently
holding the token can send messages bound the conversation.

The last message flag (`last`) is set to ``true`` only if the message is the
last message in the current conversation. Once this message is sent, the
conversation can not be used to send new messages. When the last flag (`last`)
is set to ``true``, the value of the token passing flag is ignored.

Each conversation is uniquely identified by its first message identifier and
owner flag.


Ping
----

In addition to exchanging user data, Chatter defines Ping message exchange.
The Ping communication is responsible for detecting a closed connection. This service periodically sends a Ping request and waits for a corresponding Pong
response. If the response isn't received in a defined timeout period (if the
Conversation's timeout is exceeded), the connection is closed.

This is a peer-to-peer service (there is no distinction between client and
server).

A Ping - Pong Conversation between peers contains these messages:

    +-----------------+--------------+-------------+
    |                 | Conversation |             |
    | Message         +-------+------+ Direction   |
    |                 | First | Last |             |
    +=================+=======+======+=============+
    | Ping            | T     | F    | p1 |arr| p2 |
    +-----------------+-------+------+-------------+
    | Pong            | F     | T    | p2 |arr| p1 |
    +-----------------+-------+------+-------------+

where 'p1' and 'p2' are two communicating peers.

.. |arr| unicode:: U+003E


API
---

API reference is available as part of generated documentation:

    * `Python hat.drivers.chatter module <py_api/hat/drivers/chatter.html>`_
