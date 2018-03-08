import api.API;
import error.BeatsException;
import org.junit.Test;

public class AllTests {

    @Test
    public void test1(){
        try {

            String config_file = "C:\\Users\\gomes\\code\\ta_solver\\configfiles\\seven_links.xml";
            Entry_Point_BeATS entry_point = new Entry_Point_BeATS();
            API api = entry_point.get_BeATS_API();
            api.load(config_file);


        } catch (BeatsException e) {
            e.printStackTrace();
        }
    }
}
