import com.comsol.model.*;
import com.comsol.model.util.*;

/** Suspended LN plate, same electrodes and crystal axes as the archived non-suspended cell. */
public class Idt2dSus {
  static final String PZ = "D:\\COMSOL63\\Multiphysics\\data\\comsol_piezo_lib.mph";
  static final String BASIC = "D:\\COMSOL63\\Multiphysics\\data\\comsol_basic_material_lib.mph";

  public static void main(String[] args) throws Exception {
    ModelUtil.initStandalone(true);
    Model model = ModelUtil.create("Model");
    model.modelPath("D:\\comsol_ao_run\\idt_2d_sus");
    model.label("idt_2d_sus.mph");
    try {
      build(model);
      double[] periods = {2.58};
      for (int i = 0; i < periods.length; i++) solve(model, periods[i]);
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

  static void build(Model model) throws Exception {
    model.param().set("p", "1[um]");
    model.param().set("hLn", "500[nm]");
    model.param().set("hAl", "100[nm]");
    model.param().set("duty", "0.25");
    model.modelNode().create("comp1");
    model.geom().create("geom1", 2);
    model.geom("geom1").lengthUnit("m");
    model.geom("geom1").feature().create("rLn", "Rectangle");
    model.geom("geom1").feature("rLn").set("size", new String[]{"p", "hLn"});
    model.geom("geom1").feature("rLn").set("pos", new String[]{"0", "0"});
    model.geom("geom1").feature().create("rAp", "Rectangle");
    model.geom("geom1").feature("rAp").set("size", new String[]{"duty*p", "hAl"});
    model.geom("geom1").feature("rAp").set("pos", new String[]{"(p-2*duty*p)/4", "hLn"});
    model.geom("geom1").feature().create("rAn", "Rectangle");
    model.geom("geom1").feature("rAn").set("size", new String[]{"duty*p", "hAl"});
    model.geom("geom1").feature("rAn").set("pos", new String[]{"p/2+(p-2*duty*p)/4", "hLn"});
    model.geom("geom1").run();

    box(model, "selLN", "1[nm]", "p-1[nm]", "1[nm]", "hLn-1[nm]");
    box(model, "selAl", "1[nm]", "p-1[nm]", "hLn+1[nm]", "hLn+hAl-1[nm]");
    box(model, "selGp", "(p-2*duty*p)/4-1[nm]", "(p-2*duty*p)/4+duty*p+1[nm]", "hLn-1[nm]", "hLn+1[nm]");
    box(model, "selGn", "p/2+(p-2*duty*p)/4-1[nm]", "p/2+(p-2*duty*p)/4+duty*p+1[nm]", "hLn-1[nm]", "hLn+1[nm]");
    model.component("comp1").selection().create("selGnd", "Union");
    model.component("comp1").selection("selGnd").set("entitydim", "1");
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
    model.physics("solid").create("pzm1", "PiezoelectricMaterialModel", 2);
    model.physics("solid").feature("pzm1").selection().named("selLN");
    model.physics("es").create("gnd1", "Ground", 1);
    model.physics("es").feature("gnd1").selection().named("selGnd");
    model.physics("solid").create("pc1", "PeriodicCondition", 1);
    model.physics("es").create("pc1", "PeriodicCondition", 1);
    applyPeriodic(model);

    model.component("comp1").cpl().create("intLN", "Integration");
    model.component("comp1").cpl("intLN").selection().geom("geom1", 2);
    model.component("comp1").cpl("intLN").selection().named("selLN");
    model.component("comp1").cpl().create("intAl", "Integration");
    model.component("comp1").cpl("intAl").selection().geom("geom1", 2);
    model.component("comp1").cpl("intAl").selection().named("selAl");

    model.mesh().create("mesh1", "geom1");
    size(model, "szLN", "selLN", "40[nm]", "8[nm]");
    size(model, "szAl", "selAl", "40[nm]", "8[nm]");
    model.mesh("mesh1").feature().create("ftri1", "FreeTri");
    model.mesh("mesh1").feature("ftri1").selection().geom("geom1", 2);
    model.mesh("mesh1").feature("ftri1").selection().all();
    model.mesh("mesh1").run();

    model.study().create("std1");
    model.study("std1").create("eig", "Eigenfrequency");
    model.study("std1").feature("eig").set("neigs", "12");
    model.study("std1").feature("eig").set("shift", "3.33[GHz]");
    model.study("std1").feature("eig").set("shiftactive", "on");
    model.study("std1").createAutoSequences("all");
    System.out.println("BUILD_OK");
  }

  static void box(Model model, String tag, String xmin, String xmax, String ymin, String ymax) {
    model.component("comp1").selection().create(tag, "Box");
    model.component("comp1").selection(tag).set("entitydim", tag.startsWith("selG") ? "1" : "2");
    model.component("comp1").selection(tag).set("condition", "intersects");
    model.component("comp1").selection(tag).set("xmin", xmin);
    model.component("comp1").selection(tag).set("xmax", xmax);
    model.component("comp1").selection(tag).set("ymin", ymin);
    model.component("comp1").selection(tag).set("ymax", ymax);
  }

  static int[] sideEdges(Model model, boolean lnOnly) {
    int nE = model.geom("geom1").getNEdges();
    int[] left = new int[nE];
    int[] right = new int[nE];
    int nl = 0;
    int nr = 0;
    double pmax = 0;
    for (int e = 1; e <= nE; e++) {
      double[][] a = model.geom("geom1").edgeX(e, new double[]{0.5});
      pmax = Math.max(pmax, a[0][0]);
    }
    for (int e = 1; e <= nE; e++) {
      double[][] a = model.geom("geom1").edgeX(e, new double[]{0.02, 0.98});
      double x0 = a[0][0];
      double y0 = a[0][1];
      double x1 = a[1][0];
      double y1 = a[1][1];
      if (Math.abs(x0 - x1) > 1e-10 || Math.abs(y0 - y1) < 1e-10) continue;
      double ylo = Math.min(y0, y1);
      double yhi = Math.max(y0, y1);
      if (lnOnly && (ylo < -1e-9 || yhi > 500e-9 + 1e-9)) continue;
      if (Math.abs(x0) < 1e-9) left[nl++] = e;
      if (Math.abs(x0 - pmax) < 1e-9) right[nr++] = e;
    }
    int[] use = new int[nl + nr];
    System.arraycopy(left, 0, use, 0, nl);
    System.arraycopy(right, 0, use, nl, nr);
    return use;
  }

  static void applyPeriodic(Model model) {
    int[] solid = sideEdges(model, false);
    int[] es = sideEdges(model, true);
    System.out.println("VERT solid=" + solid.length + " es=" + es.length);
    model.physics("solid").feature("pc1").selection().set(solid);
    model.physics("es").feature("pc1").selection().set(es);
  }

  static void size(Model model, String tag, String sel, String hmax, String hmin) {
    model.mesh("mesh1").feature().create(tag, "Size");
    model.mesh("mesh1").feature(tag).selection().geom("geom1", 2);
    model.mesh("mesh1").feature(tag).selection().named(sel);
    model.mesh("mesh1").feature(tag).set("hmaxactive", "on");
    model.mesh("mesh1").feature(tag).set("hminactive", "on");
    model.mesh("mesh1").feature(tag).set("hmax", hmax);
    model.mesh("mesh1").feature(tag).set("hmin", hmin);
  }

  static void solve(Model model, double pUm) {
    System.out.println("SOLVE p_um=" + pUm);
    try {
      model.param().set("p", pUm + "[um]");
      model.geom("geom1").run();
      applyPeriodic(model);
      model.component("comp1").cpl("intLN").selection().named("selLN");
      model.component("comp1").cpl("intAl").selection().named("selAl");
      model.mesh("mesh1").run();
      model.study("std1").run();
      try { model.result().numerical().remove("gev1"); } catch (Exception ex) {}
      model.result().numerical().create("gev1", "EvalGlobal");
      model.result().numerical("gev1").set("expr", new String[]{
        "freq", "intLN(solid.Ws)", "intAl(solid.Ws)", "intLN(u^2)", "intLN(v^2)"
      });
      model.result().numerical("gev1").set("looplevelinput", new String[]{"all"});
      double[][] re = model.result().numerical("gev1").getReal();
      int nMode = re[0].length;
      double k = 2 * Math.PI / (pUm * 1e-6);
      for (int m = 0; m < nMode; m++) {
        double f = re[0][m];
        double eL = Math.abs(re[1][m]);
        double eA = Math.abs(re[2][m]);
        double u2 = Math.abs(re[3][m]);
        double v2 = Math.abs(re[4][m]);
        double et = eL + eA;
        double ut = u2 + v2;
        System.out.println(String.format(java.util.Locale.US,
            "ROW p_um=%.4f f_GHz=%.6f k_rad_m=%.6e fracLN=%.4f fracAl=%.4f pu=%.3f pv=%.3f",
            pUm, f / 1e9, k, et > 0 ? eL / et : -1, et > 0 ? eA / et : -1,
            ut > 0 ? u2 / ut : -1, ut > 0 ? v2 / ut : -1));
      }
    } catch (Throwable ex) {
      System.out.println("FAIL p_um=" + pUm);
      ex.printStackTrace(System.out);
    }
  }
}
