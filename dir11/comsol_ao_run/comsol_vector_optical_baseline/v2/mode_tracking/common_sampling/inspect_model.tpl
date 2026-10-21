import com.comsol.model.*;
import com.comsol.model.util.*;

/**
 * Read-only inspector for a saved optical model: prints what the model
 * ACTUALLY contains, so configuration is never inferred from a file name.
 * Nothing is solved and nothing is saved.
 */
public class __CLASS__ {
  static void p(String k, Object v) { System.out.println("CHK " + k + " = " + v); }

  static String arr(double[] v) {
    StringBuilder s = new StringBuilder("[");
    for (int i = 0; i < v.length; i++) {
      if (i > 0) s.append(", ");
      s.append(String.format(java.util.Locale.US, "%.10g", v[i]));
    }
    return s.append("]").toString();
  }

  static String arr(String[] v) {
    StringBuilder s = new StringBuilder("[");
    for (int i = 0; i < v.length; i++) {
      if (i > 0) s.append(", ");
      s.append(v[i]);
    }
    return s.append("]").toString();
  }

  static String arr(int[] v) {
    StringBuilder s = new StringBuilder("[");
    for (int i = 0; i < v.length; i++) {
      if (i > 0) s.append(", ");
      s.append(v[i]);
    }
    return s.append("]").toString();
  }

  public static void main(String[] args) throws Exception {
    ModelUtil.initStandalone(true);
    Model m = ModelUtil.load("m", "__MODEL__");
    p("FILE", "__MODEL__");

    ModelNode c = m.component("comp1");

    try {
      p("GEOM_ndomains", c.geom("geom1").getNDomains());
      p("GEOM_lengthUnit", c.geom("geom1").lengthUnit());
    } catch (Throwable t) { p("GEOM_FAILED", t.getMessage()); }

    String[] mats = c.material().tags();
    p("MAT_list", mats == null ? "" : java.util.Arrays.toString(mats));

    for (String t : mats) {
      try {
        p("MAT_" + t + "_entities", arr(c.material(t).selection().entities()));
      } catch (Throwable e) { p("MAT_" + t + "_entities", "FAILED " + e.getMessage()); }
      String[] keys = new String[]{"relpermittivity", "electricconductivity",
                                   "relpermeability"};
      for (String k : keys) {
        try {
          p("MAT_" + t + "_" + k,
            arr(c.material(t).propertyGroup("def").getStringArray(k)));
        } catch (Throwable e1) {
          try {
            p("MAT_" + t + "_" + k,
              c.material(t).propertyGroup("def").getString(k));
          } catch (Throwable e2) {
            p("MAT_" + t + "_" + k, "UNREADABLE");
          }
        }
      }
    }

    try {
      p("PHYS_list", c.physics().tags() == null ? "" :
                     java.util.Arrays.toString(c.physics().tags()));
      p("PHYS_DisplacementFieldModel",
        c.physics("ewfd").feature("wee1").getString("DisplacementFieldModel"));
    } catch (Throwable t) {
      try {
        p("PHYS_DisplacementFieldModel",
          arr(c.physics("ewfd").feature("wee1")
              .getStringArray("DisplacementFieldModel")));
      } catch (Throwable t2) { p("PHYS_DisplacementFieldModel", "UNREADABLE"); }
    }

    try {
      p("MESH_tri", c.mesh("mesh1").getElem("tri")[0].length);
      p("MESH_hmax", c.mesh("mesh1").feature("size").getString("hmax"));
      p("MESH_hmin", c.mesh("mesh1").feature("size").getString("hmin"));
      p("MESH_hauto", c.mesh("mesh1").feature("size").getString("hauto"));
    } catch (Throwable t) { p("MESH_FAILED", t.getMessage()); }

    try {
      p("STUDY_list", java.util.Arrays.toString(m.study().tags()));
      p("STUDY_modeFreq", m.study("std1").feature("mode").getString("modeFreq"));
      p("STUDY_neigs", m.study("std1").feature("mode").getString("neigs"));
      p("STUDY_shift", m.study("std1").feature("mode").getString("shift"));
      p("STUDY_neigsactive",
        m.study("std1").feature("mode").getString("neigsactive"));
      p("STUDY_shiftactive",
        m.study("std1").feature("mode").getString("shiftactive"));
    } catch (Throwable t) { p("STUDY_FAILED", t.getMessage()); }

    try {
      p("SOL_list", java.util.Arrays.toString(m.sol().tags()));
      for (String st : m.sol().tags()) {
        p("SOL_" + st + "_size", arr(m.sol(st).getSize()));
      }
    } catch (Throwable t) { p("SOL_FAILED", t.getMessage()); }

    try {
      p("DSET_list", java.util.Arrays.toString(m.result().dataset().tags()));
    } catch (Throwable t) { p("DSET_FAILED", t.getMessage()); }

    System.out.println("INSPECT_DONE");
    ModelUtil.disconnect();
  }
}
