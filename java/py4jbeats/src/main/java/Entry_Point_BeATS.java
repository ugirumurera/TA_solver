import py4j.GatewayServer;

public class Entry_Point_BeATS {

	private api.API api;

	public Entry_Point_BeATS() {
		api = new api.API();
	}

	public api.API get_BeATS_API(){
		return api;
	}

	public static void main(String[] args) {
		try{
			GatewayServer gatewayServer;
			if(1==args.length)
				gatewayServer = new GatewayServer(new Entry_Point_BeATS(),Integer.parseInt(args[0]));
			else
				gatewayServer = new GatewayServer(new Entry_Point_BeATS());
			gatewayServer.start();
			System.out.println("Gateway Server Started on port " + gatewayServer.getPort());
			
		} catch((Py4JNetworkException e){
			System.out.println("Could not initialize Java Gateway");
			System.exit(1);
		}
	}

}
