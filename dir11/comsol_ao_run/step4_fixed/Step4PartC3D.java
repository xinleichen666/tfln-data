import com.comsol.model.*;
import com.comsol.model.util.*;
import java.lang.reflect.*;
import java.util.*;
import java.io.*;

/** Step 4 Part C, 3D check at p_new (3D-B settings: no w constraint). */
public class Step4PartC3D {
  static final String PZ = "D:\\COMSOL63\\Multiphysics\\data\\comsol_piezo_lib.mph";
  static final String BASIC = "D:\\COMSOL63\\Multiphysics\\data\\comsol_basic_material_lib.mph";
  static final String PNEW = "D:\\comsol_ao_run\\step4_fixed\\pnew.txt";
  static final double FGOAL = 3.33;

  public static void main(String[] args) {
    try {
      ModelUtil.initStandalone(true);
      System.out.println("STEP4_C3D_START");
      double pNew = 2.85261315;
      double f2D = 3.329955;
      System.out.println(String.format(Locale.US, "PNEW_INPUT p_um=%.10f f_2D_GHz=%.6f", pNew, f2D));
      Model model = ModelUtil.create("M4C3D");
      build(model, pNew);
      solve(model, pNew, f2D);
      ModelUtil.remove("M4C3D");
      System.out.println("STEP4_C3D_DONE");
    } catch (Throwable t) {
      System.out.println("STEP4_C3D_ABORT");
      t.printStackTrace(System.out);
    }
  }

  static void copyGroup(Material dst, Material src, String group, boolean create) {
    if (create) dst.propertyGroup().create(group, group);
    String[] names = src.propertyGroup(group).properties();
    for (int i = 0; i < names.length; i++) {
      try { dst.propertyGroup(group).set(names[i], src.propertyGroup(group).getStringArray(names[i])); }
      catch (Exception ex) { System.out.println("skip " + group + "." + names[i]); }
    }
  }
  static void block(Model model, String tag, String sx, String sy, String sz, String px, String py, String pz) {
    model.geom("geom1").feature().create(tag, "Block");
    model.geom("geom1").feature(tag).set("size", new String[]{sx, sy, sz});
    model.geom("geom1").feature(tag).set("pos", new String[]{px, py, pz});
  }
  static void box(Model model, String tag, int dim, String xmin, String xmax, String ymin, String ymax,
                  String zmin, String zmax, String cond) {
    model.component("comp1").selection().create(tag, "Box");
    model.component("comp1").selection(tag).set("entitydim", Integer.toString(dim));
    model.component("comp1").selection(tag).set("condition", cond);
    model.component("comp1").selection(tag).set("xmin", xmin);
    model.component("comp1").selection(tag).set("xmax", xmax);
    model.component("comp1").selection(tag).set("ymin", ymin);
    model.component("comp1").selection(tag).set("ymax", ymax);
    model.component("comp1").selection(tag).set("zmin", zmin);
    model.component("comp1").selection(tag).set("zmax", zmax);
  }
  static int nSel(Model model, String tag) {
    try { return model.component("comp1").selection(tag).entities().length; } catch (Throwable t) { return -1; }
  }
  static String getStr(Object o, String n) {
    try { return (String) o.getClass().getMethod("getString", String.class).invoke(o, n); } catch (Throwable t) { return "ERR"; }
  }
  static void setStr(Object o, String n, String v) throws Exception { o.getClass().getMethod("set", String.class, String.class).invoke(o, n, v); }
  static void setArr(Object o, String n, String[] v) throws Exception { o.getClass().getMethod("set", String.class, String[].class).invoke(o, n, v); }
  static String oneLine(Throwable ex) {
    Throwable c = (ex instanceof InvocationTargetException) ? ((InvocationTargetException) ex).getTargetException() : ex;
    String s = c.getClass().getSimpleName() + ": " + String.valueOf(c.getMessage());
    s = s.replace('\n', ' ').replace('\r', ' ').replace(',', ';');
    return s.length() > 220 ? s.substring(0, 220) : s;
  }

  static void build(Model model, double pUm) throws Exception {
    model.param().set("p", String.format(Locale.US, "%.10f[um]", pUm));
    model.param().set("hLn", "500[nm]");
    model.param().set("hAl", "100[nm]");
    model.param().set("duty", "0.25");
    model.param().set("Lz", "0.5[um]");
    model.param().set("Wstack", "Lz");
    model.param().set("z0", "0");
    model.param().set("Wap", "Lz");
    model.modelNode().create("comp1");
    model.geom().create("geom1", 3);
    model.geom("geom1").lengthUnit("m");
    block(model, "bLn", "p", "hLn", "Wstack", "0", "0", "0");
    block(model, "bAp", "duty*p", "hAl", "Wap", "(p-2*duty*p)/4", "hLn", "z0");
    block(model, "bAn", "duty*p", "hAl", "Wap", "p/2+(p-2*duty*p)/4", "hLn", "z0");
    model.geom("geom1").run();
    box(model, "selLN", 3, "1[nm]", "p-1[nm]", "1[nm]", "hLn-1[nm]", "1[nm]", "Wstack-1[nm]", "intersects");
    box(model, "selAl", 3, "1[nm]", "p-1[nm]", "hLn+1[nm]", "hLn+hAl-1[nm]", "z0+1[nm]", "z0+Wap-1[nm]", "intersects");
    box(model, "selGp", 2, "(p-2*duty*p)/4-1[nm]", "(p-2*duty*p)/4+duty*p+1[nm]", "hLn-1[nm]", "hLn+1[nm]", "z0-1[nm]", "z0+Wap+1[nm]", "inside");
    box(model, "selGn", 2, "p/2+(p-2*duty*p)/4-1[nm]", "p/2+(p-2*duty*p)/4+duty*p+1[nm]", "hLn-1[nm]", "hLn+1[nm]", "z0-1[nm]", "z0+Wap+1[nm]", "inside");
    System.out.println("GROUND_CHECK selGp=" + nSel(model, "selGp") + " selGn=" + nSel(model, "selGn"));
    if (nSel(model, "selGp") != 1 || nSel(model, "selGn") != 1) throw new RuntimeException("ground check failed");
    model.component("comp1").selection().create("selGnd", "Union");
    model.component("comp1").selection("selGnd").set("entitydim", "2");
    model.component("comp1").selection("selGnd").set("input", new String[]{"selGp", "selGn"});
    Model pz = ModelUtil.load("pz", PZ);
    Model basic = ModelUtil.load("basic", BASIC);
    Material ln = model.component("comp1").material().create("matLN", "Common");
    ln.selection().named("selLN");
    copyGroup(ln, pz.material("lithium_niobate"), "def", false);
    copyGroup(ln, pz.material("lithium_niobate"), "StressCharge", true);
    Material al = model.component("comp1").material().create("matAl", "Common");
    al.selection().named("selAl");
    copyGroup(al, basic.material("aluminum"), "def", false);
    copyGroup(al, basic.material("aluminum"), "Enu", true);
    ModelUtil.remove("pz"); ModelUtil.remove("basic");
    model.physics().create("solid", "SolidMechanics", "geom1");
    model.physics().create("es", "Electrostatics", "geom1");
    model.physics("es").selection().named("selLN");
    model.multiphysics().create("pze1", "PiezoelectricEffect", "geom1");
    model.physics("solid").create("pzm1", "PiezoelectricMaterialModel", 3);
    model.physics("solid").feature("pzm1").selection().named("selLN");
    model.physics("es").create("ccp1", "ChargeConservationPiezo", 3);
    model.physics("es").feature("ccp1").selection().named("selLN");
    Object sys = model.component("comp1").coordSystem().create("sys2", "Rotated");
    setStr(sys, "rotationSequence", "ZXZ");
    setArr(sys, "angle", new String[]{"90[deg]", "0", "0"});
    setStr(model.physics("solid").feature("pzm1"), "coordinateSystem", "sys2");
    setStr(model.physics("es").feature("ccp1"), "coordinateSystem", "sys2");
    System.out.println("COORD_SYS_SET pzm1=" + getStr(model.physics("solid").feature("pzm1"), "coordinateSystem")
        + " ccp1=" + getStr(model.physics("es").feature("ccp1"), "coordinateSystem"));
    model.physics("solid").feature("pzm1").create("dmp1", "Damping", 3);
    model.physics("solid").feature("pzm1").feature("dmp1").set("DampingType", "IsotropicLossFactor");
    model.physics("solid").feature("pzm1").feature("dmp1").set("eta_s_mat", "userdef");
    model.physics("solid").feature("pzm1").feature("dmp1").set("eta_s", "5e-4");
    model.physics("solid").prop("ShapeProperty").set("order_displacement", "2");
    System.out.println("ORDER_READBACK order=" + getStr(model.physics("solid").prop("ShapeProperty"), "order_displacement"));
    model.physics("es").create("gnd1", "Ground", 2);
    model.physics("es").feature("gnd1").selection().named("selGnd");
    box(model, "selLeft", 2, "-1[nm]", "1[nm]", "-1[nm]", "hLn+hAl+1[nm]", "-1[nm]", "Wstack+1[nm]", "inside");
    box(model, "selRight", 2, "p-1[nm]", "p+1[nm]", "-1[nm]", "hLn+hAl+1[nm]", "-1[nm]", "Wstack+1[nm]", "inside");
    box(model, "selLeftE", 2, "-1[nm]", "1[nm]", "-1[nm]", "hLn+1[nm]", "-1[nm]", "Wstack+1[nm]", "inside");
    box(model, "selRightE", 2, "p-1[nm]", "p+1[nm]", "-1[nm]", "hLn+1[nm]", "-1[nm]", "Wstack+1[nm]", "inside");
    model.component("comp1").selection().create("selPer", "Union");
    model.component("comp1").selection("selPer").set("entitydim", "2");
    model.component("comp1").selection("selPer").set("input", new String[]{"selLeft", "selRight"});
    model.component("comp1").selection().create("selPerE", "Union");
    model.component("comp1").selection("selPerE").set("entitydim", "2");
    model.component("comp1").selection("selPerE").set("input", new String[]{"selLeftE", "selRightE"});
    box(model, "selZ0", 2, "-1[nm]", "p+1[nm]", "-1[nm]", "hLn+hAl+1[nm]", "-1[nm]", "1[nm]", "inside");
    box(model, "selZ1", 2, "-1[nm]", "p+1[nm]", "-1[nm]", "hLn+hAl+1[nm]", "Lz-1[nm]", "Lz+1[nm]", "inside");
    box(model, "selZ0E", 2, "-1[nm]", "p+1[nm]", "-1[nm]", "hLn+1[nm]", "-1[nm]", "1[nm]", "inside");
    box(model, "selZ1E", 2, "-1[nm]", "p+1[nm]", "-1[nm]", "hLn+1[nm]", "Lz-1[nm]", "Lz+1[nm]", "inside");
    model.component("comp1").selection().create("selPerZ", "Union");
    model.component("comp1").selection("selPerZ").set("entitydim", "2");
    model.component("comp1").selection("selPerZ").set("input", new String[]{"selZ0", "selZ1"});
    model.component("comp1").selection().create("selPerZE", "Union");
    model.component("comp1").selection("selPerZE").set("entitydim", "2");
    model.component("comp1").selection("selPerZE").set("input", new String[]{"selZ0E", "selZ1E"});
    model.physics("solid").create("pc1", "PeriodicCondition", 2);
    model.physics("solid").feature("pc1").selection().named("selPer");
    model.physics("es").create("pc1", "PeriodicCondition", 2);
    model.physics("es").feature("pc1").selection().named("selPerE");
    model.physics("solid").create("pc2", "PeriodicCondition", 2);
    model.physics("solid").feature("pc2").selection().named("selPerZ");
    model.physics("es").create("pc2", "PeriodicCondition", 2);
    model.physics("es").feature("pc2").selection().named("selPerZE");
    model.component("comp1").cpl().create("intLN", "Integration");
    model.component("comp1").cpl("intLN").selection().geom("geom1", 3);
    model.component("comp1").cpl("intLN").selection().named("selLN");
    model.component("comp1").cpl().create("intAl", "Integration");
    model.component("comp1").cpl("intAl").selection().geom("geom1", 3);
    model.component("comp1").cpl("intAl").selection().named("selAl");
    model.mesh().create("mesh1", "geom1");
    size(model, "szLN", "selLN", "75[nm]", "20[nm]");
    size(model, "szAl", "selAl", "40[nm]", "10[nm]");
    model.mesh("mesh1").feature().create("ftet1", "FreeTet");
    model.mesh("mesh1").feature("ftet1").selection().geom("geom1", 3);
    model.mesh("mesh1").feature("ftet1").selection().all();
    model.mesh("mesh1").run();
    System.out.println("NUMELEM n_elem=" + model.mesh("mesh1").getNumElem());
    model.study().create("stdE");
    model.study("stdE").create("eig", "Eigenfrequency");
    model.study("stdE").feature("eig").set("neigs", "24");
    model.study("stdE").feature("eig").set("shift", "3.0[GHz]");
    model.study("stdE").feature("eig").set("shiftactive", "on");
    model.study("stdE").createAutoSequences("all");
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

  static void solve(Model model, double pUm, double f2D) {
    model.study("stdE").run();
    model.result().numerical().create("gev1", "EvalGlobal");
    model.result().numerical("gev1").set("expr", new String[]{
      "freq", "intLN(solid.Ws)", "intAl(solid.Ws)", "intLN(u^2)", "intLN(v^2)", "intLN(w^2)"});
    model.result().numerical("gev1").set("looplevelinput", new String[]{"all"});
    double[][] re = model.result().numerical("gev1").getReal();
    double[][] im = model.result().numerical("gev1").getImag();
    int n = re[0].length;
    List<double[]> rows = new ArrayList<double[]>();
    for (int m = 0; m < n; m++) {
      double f = re[0][m], fi = im[0][m];
      double eL = Math.abs(re[1][m]), eA = Math.abs(re[2][m]);
      double u2 = Math.abs(re[3][m]), v2 = Math.abs(re[4][m]), w2 = Math.abs(re[5][m]);
      double et = eL + eA, ut = u2 + v2 + w2;
      double[] r = new double[]{f / 1e9, fi / 1e6, et > 0 ? eL / et : -1, et > 0 ? eA / et : -1,
        ut > 0 ? u2 / ut : -1, ut > 0 ? v2 / ut : -1, ut > 0 ? w2 / ut : -1};
      rows.add(r);
      System.out.println(String.format(Locale.US,
          "ROW variant=3D-B-pnew p_um=%.10f dim=3 part=C f_GHz=%.6f fi_MHz=%.4f fracLN=%.4f fracAl=%.4f pu=%.3f pv=%.3f pw=%.3f orient=sys",
          pUm, r[0], r[1], r[2], r[3], r[4], r[5], r[6]));
    }
    double[] best = null; double bd = 1e9;
    for (int i = 0; i < rows.size(); i++) {
      double[] r = rows.get(i);
      if (r[5] >= 0.80 && r[2] >= 0.93 && r[0] >= 3.0 && r[0] <= 3.7) {
        double d = Math.abs(r[0] - FGOAL);
        if (d < bd) { bd = d; best = r; }
      }
    }
    if (best == null) { System.out.println("C3D_TARGET NA"); return; }
    double[] pa = null; double pd = 30.0;
    for (int i = 0; i < rows.size(); i++) {
      double[] r = rows.get(i);
      if (r == best || r[5] < 0.80) continue;
      double d = Math.abs(r[0] - best[0]) * 1000.0;
      if (d > 0 && d < pd) { pd = d; pa = r; }
    }
    double diff = Math.abs(best[0] - f2D) / Math.abs(f2D);
    System.out.println(String.format(Locale.US,
        "C3D_TARGET f_target_GHz=%.6f pv=%.3f pw=%.3f fracAl=%.4f f_partner_GHz=%s f_2D_GHz=%.6f rel_diff_%%=%.6f <0.3%%=%s",
        best[0], best[5], best[6], best[3], pa == null ? "NA" : String.format(Locale.US, "%.6f", pa[0]),
        f2D, diff * 100.0, (diff < 0.003)));
  }
}
