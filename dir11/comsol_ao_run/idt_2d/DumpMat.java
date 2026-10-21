import com.comsol.model.*;
import com.comsol.model.util.*;

public class DumpMat {
  static void dump(Model m, String tag) {
    System.out.println("==== " + tag + " | " + m.material(tag).label());
    String[] pgs = m.material(tag).propertyGroup().tags();
    for (int i = 0; i < pgs.length; i++) {
      System.out.println("PG " + pgs[i]);
      try {
        String[] names = m.material(tag).propertyGroup(pgs[i]).properties();
        for (int j = 0; j < names.length; j++) {
          String v = "";
          try {
            String[] arr = m.material(tag).propertyGroup(pgs[i]).getStringArray(names[j]);
            StringBuilder sb = new StringBuilder();
            for (int k = 0; k < arr.length; k++) {
              if (k > 0) sb.append(" | ");
              sb.append(arr[k]);
            }
            v = sb.toString();
          } catch (Exception ex) {
            v = "ERR " + ex.getClass().getSimpleName();
          }
          System.out.println("  " + names[j] + " = " + v);
        }
      } catch (Exception ex) {
        System.out.println("  properties() " + ex);
      }
    }
  }

  public static void main(String[] args) throws Exception {
    ModelUtil.initStandalone(true);
    Model pz = ModelUtil.load("pz", "D:\\COMSOL63\\Multiphysics\\data\\comsol_piezo_lib.mph");
    Model basic = ModelUtil.load("basic", "D:\\COMSOL63\\Multiphysics\\data\\comsol_basic_material_lib.mph");
    Model mems = ModelUtil.load("mems", "D:\\COMSOL63\\Multiphysics\\data\\comsol_mems_lib.mph");
    dump(pz, "lithium_niobate");
    dump(basic, "aluminum");
    dump(mems, "sio2_-_silicon_oxide");
    dump(mems, "si_-_silicon_(single-crystal,_anisotropic)");
    dump(basic, "silicon");
  }
}
