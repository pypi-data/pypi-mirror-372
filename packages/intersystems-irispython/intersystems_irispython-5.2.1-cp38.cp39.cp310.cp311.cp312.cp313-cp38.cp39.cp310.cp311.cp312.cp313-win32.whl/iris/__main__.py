import sys
import iris

if len(sys.argv) >= 2 and sys.argv[1] == "PythonGateway":
    iris.startGatewayServer(*sys.argv[2:])
else:
    print("Invalid Parameter")
