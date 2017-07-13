import py4j.GatewayServer;
import py4j.Py4JNetworkException;

import java.net.InetAddress;

public class Entry_Point_BeATS {

	private api.API api;

	public Entry_Point_BeATS() {
		api = new api.API();
	}

	public api.API get_BeATS_API(){
		return api;
	}

	public static void main(String[] args) throws Exception {
		GatewayServer gatewayServer=null;
		try{
//			InetAddress s = gatewayServer.getAddress();
			if(1==args.length)
				gatewayServer = new GatewayServer(new Entry_Point_BeATS(),Integer.parseInt(args[0]));
			else
				gatewayServer = new GatewayServer(new Entry_Point_BeATS());
			gatewayServer.start();
			System.out.println("Gateway Server Started on port " + gatewayServer.getPort());

		} catch(Exception e){
			if(gatewayServer!=null)
				gatewayServer.shutdown();
			throw new Exception("Could not initialize Java Gateway");
		}
	}

}
