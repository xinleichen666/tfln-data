import com.comsol.model.*;
import com.comsol.model.util.*;

public class ListMat {
  public static void main(String[] args) throws Exception {
    ModelUtil.initStandalone(true);
    String[] files = {
      "D:\\COMSOL63\\Multiphysics\\data\\comsol_piezo_lib.mph",
      "D:\\COMSOL63\\Multiphysics\\data\\comsol_basic_material_lib.mph",
      "D:\\COMSOL63\\Multiphysics\\data\\comsol_mems_lib.mph"
    };
    for (int f = 0; f < files.length; f++) {
      System.out.println("FILE " + files[f]);
      Model m = ModelUtil.load("lib" + f, files[f]);
      String[] tags = m.material().tags();
      for (int i = 0; i < tags.length; i++) {
        String lab = "";
        try { lab = m.material(tags[i]).label(); } catch (Exception ex) { lab = "?"; }
        String low = (tags[i] + " " + lab).toLowerCase();
        if (low.contains("niob") || low.contains("alumin") || low.contains("silicon")
            || low.contains("silica") || low.contains("sio2") || low.contains("quartz")) {
          System.out.println("MAT " + tags[i] + " | " + lab);
        }
      }
      ModelUtil.remove("lib" + f);
    }
  }
}
