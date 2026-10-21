import com.comsol.model.*;
import com.comsol.model.util.*;

public class CoordProbe {
  public static void main(String[] args) throws Exception {
    ModelUtil.initStandalone(true);
    Model model = ModelUtil.create("Model");
    model.modelNode().create("comp1");
    model.geom().create("geom1", 2);
    model.component("comp1").coordSystem().create("rot1", "Rotated");
    String[] props = model.component("comp1").coordSystem("rot1").properties();
    for (int i = 0; i < props.length; i++) {
      String val = "";
      try {
        val = model.component("comp1").coordSystem("rot1").getString(props[i]);
      } catch (Exception ex) {
        val = "s:" + ex.getClass().getSimpleName();
      }
      System.out.println("CS " + props[i] + " = " + val);
    }
  }
}
