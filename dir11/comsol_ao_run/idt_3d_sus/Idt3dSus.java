import com.comsol.model.*;
import com.comsol.model.util.*;

/** Suspended 3D IDT. Period from the 2D suspended vertical mode. */
public class Idt3dSus {
  static final String PZ = "D:\\COMSOL63\\Multiphysics\\data\\comsol_piezo_lib.mph";
  static final String BASIC = "D:\\COMSOL63\\Multiphysics\\data\\comsol_basic_material_lib.mph";

  public static void main(String[] args) throws Exception {
    ModelUtil.initStandalone(true);
    Model model = ModelUtil.create("Model");
    model.modelPath("D:\\comsol_ao_run\\idt_3d_sus");
    model.label("idt_3d_sus.mph");
    try {
      build(model);
      solve(model);
    } catch (Throwable ex) {
      ex.printStackTrace(System.out);
    }
  }

  static void copyGroup(Material dst, Material src, String group, boolean create) {
    if (create) dst.propertyGroup().create(group, group);
    String[] names = src.propertyGroup(group).properties();
    for (int i = 0; i < names.length; i++) {
      try {
        dst.propertyGroup(group).set(names[i], src.propertyGroup(group).getStringArray(names[i]));
      } catch (Exception ex) {
        System.out.println("skip " + group + "." + names[i]);
      }
    }
  }

  static void block(Model model, String tag, String sx, String sy, String sz, String px, String py, String pz) {
    model.geom("geom1").feature().create(tag, "Block");
    model.geom("geom1").feature(tag).set("size", new String[]{sx, sy, sz});
    model.geom("geom1").feature(tag).set("pos", new String[]{px, py, pz});
  }

  static void box(Model model, String tag, int dim, String xmin, String xmax, String ymin, String ymax, String zmin, String zmax) {
    model.component("comp1").selection().create(tag, "Box");
    model.component("comp1").selection(tag).set("entitydim", Integer.toString(dim));
    model.component("comp1").selection(tag).set("condition", "intersects");
    model.component("comp1").selection(tag).set("xmin", xmin);
    model.component("comp1").selection(tag).set("xmax", xmax);
    model.component("comp1").selection(tag).set("ymin", ymin);
    model.component("comp1").selection(tag).set("ymax", ymax);
    model.component("comp1").selection(tag).set("zmin", zmin);
    model.component("comp1").selection(tag).set("zmax", zmax);
  }

  static void build(Model model) throws Exception {
    model.param().set("p", "2.58[um]");
    model.param().set("hLn", "500[nm]");
    model.param().set("hAl", "100[nm]");
    model.param().set("duty", "0.25");
    model.param().set("Wap", "10[um]");
    model.param().set("z0", "2[um]");
    model.param().set("Wstack", "14[um]");
    model.modelNode().create("comp1");
    model.geom().create("geom1", 3);
    model.geom("geom1").lengthUnit("m");
    block(model, "bLn", "p", "hLn", "Wstack", "0", "0", "0");
    block(model, "bAp", "duty*p", "hAl", "Wap", "(p-2*duty*p)/4", "hLn", "z0");
    block(model, "bAn", "duty*p", "hAl", "Wap", "p/2+(p-2*duty*p)/4", "hLn", "z0");
    model.geom("geom1").run();

    box(model, "selLN", 3, "1[nm]", "p-1[nm]", "1[nm]", "hLn-1[nm]", "1[nm]", "Wstack-1[nm]");
    box(model, "selAl", 3, "1[nm]", "p-1[nm]", "hLn+1[nm]", "hLn+hAl-1[nm]", "z0+1[nm]", "z0+Wap-1[nm]");
    box(model, "selGp", 2, "(p-2*duty*p)/4-1[nm]", "(p-2*duty*p)/4+duty*p+1[nm]",
        "hLn-1[nm]", "hLn+1[nm]", "z0-1[nm]", "z0+Wap+1[nm]");
    box(model, "selGn", 2, "p/2+(p-2*duty*p)/4-1[nm]", "p/2+(p-2*duty*p)/4+duty*p+1[nm]",
        "hLn-1[nm]", "hLn+1[nm]", "z0-1[nm]", "z0+Wap+1[nm]");
    model.component("comp1").selection("selGp").set("condition", "intersects");
    model.component("comp1").selection("selGn").set("condition", "intersects");
    model.component("comp1").selection().create("selGnd", "Union");
    model.component("comp1").selection("selGnd").set("entitydim", "2");
    model.component("comp1").selection("selGnd").set("input", new String[]{"selGp", "selGn"});

    Model pz = ModelUtil.load("pz", PZ);
    Model basic = ModelUtil.load("basic", BASIC);
    Material ln = model.component("comp1").material().create("matLN", "Common");
    ln.label("Lithium Niobate");
    ln.selection().named("selLN");
    ln.set("basis", "on");
    ln.set("basisx", new String[]{"0", "1", "0"});
    ln.set("specifybasisy", "on");
    ln.set("basisy", new String[]{"-1", "0", "0"});
    copyGroup(ln, pz.material("lithium_niobate"), "def", false);
    copyGroup(ln, pz.material("lithium_niobate"), "StressCharge", true);
    Material al = model.component("comp1").material().create("matAl", "Common");
    al.label("Aluminum");
    al.selection().named("selAl");
    copyGroup(al, basic.material("aluminum"), "def", false);
    copyGroup(al, basic.material("aluminum"), "Enu", true);
    ModelUtil.remove("pz");
    ModelUtil.remove("basic");

    model.physics().create("solid", "SolidMechanics", "geom1");
    model.physics().create("es", "Electrostatics", "geom1");
    model.physics("es").selection().named("selLN");
    model.multiphysics().create("pze1", "PiezoelectricEffect", "geom1");
    model.physics("solid").create("pzm1", "PiezoelectricMaterialModel", 3);
    model.physics("solid").feature("pzm1").selection().named("selLN");
    try { model.physics("solid").prop("ShapeProperty").set("order_displacement", "1"); }
    catch (Exception ex) { System.out.println("order " + ex.getMessage()); }
    model.physics("es").create("gnd1", "Ground", 2);
    model.physics("es").feature("gnd1").selection().named("selGnd");

    box(model, "selLeft", 2, "-1[nm]", "1[nm]", "-1[nm]", "hLn+hAl+1[nm]", "-1[nm]", "Wstack+1[nm]");
    box(model, "selRight", 2, "p-1[nm]", "p+1[nm]", "-1[nm]", "hLn+hAl+1[nm]", "-1[nm]", "Wstack+1[nm]");
    box(model, "selLeftE", 2, "-1[nm]", "1[nm]", "-1[nm]", "hLn+1[nm]", "-1[nm]", "Wstack+1[nm]");
    box(model, "selRightE", 2, "p-1[nm]", "p+1[nm]", "-1[nm]", "hLn+1[nm]", "-1[nm]", "Wstack+1[nm]");
    model.component("comp1").selection("selLeft").set("condition", "inside");
    model.component("comp1").selection("selRight").set("condition", "inside");
    model.component("comp1").selection("selLeftE").set("condition", "inside");
    model.component("comp1").selection("selRightE").set("condition", "inside");
    System.out.println("Nleft " + model.component("comp1").selection("selLeft").entities().length
        + " Nright " + model.component("comp1").selection("selRight").entities().length
        + " NleftE " + model.component("comp1").selection("selLeftE").entities().length);
    model.component("comp1").selection().create("selPer", "Union");
    model.component("comp1").selection("selPer").set("entitydim", "2");
    model.component("comp1").selection("selPer").set("input", new String[]{"selLeft", "selRight"});
    model.component("comp1").selection().create("selPerE", "Union");
    model.component("comp1").selection("selPerE").set("entitydim", "2");
    model.component("comp1").selection("selPerE").set("input", new String[]{"selLeftE", "selRightE"});
    model.physics("solid").create("pc1", "PeriodicCondition", 2);
    model.physics("solid").feature("pc1").selection().named("selPer");
    model.physics("es").create("pc1", "PeriodicCondition", 2);
    model.physics("es").feature("pc1").selection().named("selPerE");

    model.component("comp1").cpl().create("intLN", "Integration");
    model.component("comp1").cpl("intLN").selection().geom("geom1", 3);
    model.component("comp1").cpl("intLN").selection().named("selLN");
    model.component("comp1").cpl().create("intAl", "Integration");
    model.component("comp1").cpl("intAl").selection().geom("geom1", 3);
    model.component("comp1").cpl("intAl").selection().named("selAl");

    model.mesh().create("mesh1", "geom1");
    size(model, "szLN", "selLN", "150[nm]", "40[nm]");
    size(model, "szAl", "selAl", "80[nm]", "20[nm]");
    model.mesh("mesh1").feature().create("ftet1", "FreeTet");
    model.mesh("mesh1").feature("ftet1").selection().geom("geom1", 3);
    model.mesh("mesh1").feature("ftet1").selection().all();
    model.mesh("mesh1").run();

    model.study().create("std1");
    model.study("std1").create("eig", "Eigenfrequency");
    model.study("std1").feature("eig").set("neigs", "12");
    model.study("std1").feature("eig").set("shift", "3.33[GHz]");
    model.study("std1").feature("eig").set("shiftactive", "on");
    model.study("std1").createAutoSequences("all");
    System.out.println("BUILD_OK");
  }

  static void size(Model model, String tag, String sel, String hmax, String hmin) {
    model.mesh("mesh1").feature().create(tag, "Size");
    model.mesh("mesh1").feature(tag).selection().geom("geom1", 3);
    model.mesh("mesh1").feature(tag).selection().named(sel);
    model.mesh("mesh1").feature(tag).set("hmaxactive", "on");
    model.mesh("mesh1").feature(tag).set("hminactive", "on");
    model.mesh("mesh1").feature(tag).set("hmax", hmax);
    model.mesh("mesh1").feature(tag).set("hmin", hmin);
  }

  static void solve(Model model) {
    try {
      model.study("std1").run();
      model.result().numerical().create("gev1", "EvalGlobal");
      model.result().numerical("gev1").set("expr", new String[]{
        "freq", "intLN(solid.Ws)", "intAl(solid.Ws)", "intLN(u^2)", "intLN(v^2)", "intLN(w^2)"
      });
      model.result().numerical("gev1").set("looplevelinput", new String[]{"all"});
      double[][] re = model.result().numerical("gev1").getReal();
      int nMode = re[0].length;
      double k = 2 * Math.PI / 2.58e-6;
      for (int m = 0; m < nMode; m++) {
        double f = re[0][m];
        double eL = Math.abs(re[1][m]);
        double eA = Math.abs(re[2][m]);
        double u2 = Math.abs(re[3][m]);
        double v2 = Math.abs(re[4][m]);
        double w2 = Math.abs(re[5][m]);
        double et = eL + eA;
        double ut = u2 + v2 + w2;
        System.out.println(String.format(java.util.Locale.US,
            "ROW f_GHz=%.6f k_rad_m=%.6e fracLN=%.4f fracAl=%.4f pu=%.3f pv=%.3f pw=%.3f",
            f / 1e9, k, et > 0 ? eL / et : -1, et > 0 ? eA / et : -1,
            ut > 0 ? u2 / ut : -1, ut > 0 ? v2 / ut : -1, ut > 0 ? w2 / ut : -1));
      }
    } catch (Throwable ex) {
      System.out.println("FAIL");
      ex.printStackTrace(System.out);
    }
  }
}
