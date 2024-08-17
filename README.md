# Foxglove-VEX bridge
Middleware for VEX robots and Foxglove. To learn how to set up the connection and send messages, **[read the docs](https://foxglove-vex-docs.vercel.app/connecting-to-data)**!

# Repo overview
* ```server.py``` core of the program, script for opening a Websocket connection with Foxglove, and then acting as the bridge between your robot and Foxglove.
* ```vex_serial.py``` script for finding and reading from serial port with a VEX controller or brain connected. (Currently) only supports one connection at a time.
* ```json_schema.py``` script for building a [JSON schema](https://json-schema.org/learn/getting-started-step-by-step) object given a JSON object. Removes the need to define your payload's schema by letting the bridge infer it.
* ```mock_server.py```similar to ```server.py``` but sends mock messages. Used for debugging when I had no VEX brain with me.
