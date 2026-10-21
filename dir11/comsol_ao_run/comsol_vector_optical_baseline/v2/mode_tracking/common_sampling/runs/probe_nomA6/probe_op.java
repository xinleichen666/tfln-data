import com.comsol.model.*;
import com.comsol.model.util.*;

/** Probe: which integration-operator route actually works on a loaded model? */
public class probe_op {
  static void t(Model m, String label, String expr) {
    try {
      m.result().numerical().create("p" + Math.abs(label.hashCode()), "EvalGlobal");
      String tag = "p" + Math.abs(label.hashCode());
      m.result().numerical(tag).set("data", "dset1");
      m.result().numerical(tag).set("expr", new String[]{expr});
      m.result().numerical(tag).set("looplevelinput", new String[]{"manual"});
      m.result().numerical(tag).set("looplevel", new String[]{"40"});
      double[][] v = m.result().numerical(tag).getReal();
      System.out.println("OK " + label + " = " + String.format(java.util.Locale.US, "%.17g", v[0][0]));
    } catch (Throwable e) {
      String msg = String.valueOf(e.getMessage());
      if (msg.length() > 90) msg = msg.substring(0, 90);
      System.out.println("NO " + label + " : " + msg.replace('\n', ' '));
    }
  }

  public static void main(String[] a) throws Exception {
    ModelUtil.initStandalone(true);
    Model m = ModelUtil.load("m", "D:/comsol_ao_run/comsol_vector_optical_baseline/v2/out/final_nomA6.mph");
    ModelNode c = m.component("comp1");
    System.out.println("DSET " + m.result().dataset("dset1").getType());

    // existing solve-time operators
    t(m, "intAll(1)", "intAll(1)");
    t(m, "intRidge(1)", "intRidge(1)");

    // a coupling created now, referenced by its tag
    c.cpl().create("qiT", "Integration");
    c.cpl("qiT").selection().geom("geom1", 2);
    c.cpl("qiT").selection().named("selSlabL");
    try { System.out.println("OPNAME_default " + c.cpl("qiT").getString("opname")); }
    catch (Throwable e) { System.out.println("OPNAME_default UNREADABLE"); }
    t(m, "qiT(1)", "qiT(1)");
    t(m, "intop_qiT(1)", "intop_qiT(1)");

    try {
      c.cpl("qiT").set("opname", "qiT");
      System.out.println("OPNAME_set " + c.cpl("qiT").getString("opname"));
    } catch (Throwable e) { System.out.println("OPNAME_set FAILED"); }
    t(m, "qiT(1) after opname", "qiT(1)");

    // IntVolume
    try {
      m.result().numerical().create("ivT", "IntVolume");
      m.result().numerical("ivT").set("data", "dset1");
      m.result().numerical("ivT").selection().named("selSlabL");
      m.result().numerical("ivT").set("expr", new String[]{"1"});
      m.result().numerical("ivT").set("looplevelinput", new String[]{"manual"});
      m.result().numerical("ivT").set("looplevel", new String[]{"40"});
      double[][] v = m.result().numerical("ivT").getReal();
      System.out.println("OK IntVolume(1) = " + String.format(java.util.Locale.US, "%.17g", v[0][0]));
    } catch (Throwable e) {
      System.out.println("NO IntVolume : " + String.valueOf(e.getMessage()).replace('\n', ' '));
    }
    System.out.println("PROBE_DONE");
    ModelUtil.disconnect();
  }
}

