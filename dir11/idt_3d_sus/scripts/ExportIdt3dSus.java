import com.comsol.model.*;
import com.comsol.model.util.*;
import java.util.Locale;

/** Export per-mode displacement and strain at mesh nodes from Idt3dSus_Model.mph. */
public class ExportIdt3dSus {
  static final String MPH = "D:\\comsol_ao_run\\idt_3d_sus\\Idt3dSus_Model.mph";
  /** COMSOL batch sandbox allows writes under comsol_ao_run root, not always subfolders. */
  static final String OUT = "D:\\comsol_ao_run";

  static void println(String s) {
    System.out.println(s);
  }

  static String dataSet(Model model) {
    String[] ds = model.result().dataset().tags();
    println("DATASETS " + String.join(",", ds));
    if (ds.length == 0) throw new RuntimeException("no dataset");
    return ds[ds.length - 1];
  }

  static int modeCount(Model model) throws Exception {
    try {
      model.result().numerical().remove("gevFreq");
    } catch (Exception ex) { /* ignore */ }
    model.result().numerical().create("gevFreq", "EvalGlobal");
    model.result().numerical("gevFreq").set("expr", new String[]{"freq"});
    model.result().numerical("gevFreq").set("looplevelinput", new String[]{"all"});
    double[][] re = model.result().numerical("gevFreq").getReal();
    return re[0].length;
  }

  static void writeSummary(Model model, int nMode, String ds) throws Exception {
    try {
      model.result().numerical().remove("gevSum");
    } catch (Exception ex) { /* ignore */ }
    model.result().numerical().create("gevSum", "EvalGlobal");
    model.result().numerical("gevSum").set("data", ds);
    model.result().numerical("gevSum").set("expr", new String[]{
        "freq", "intLN(solid.Ws)", "intAl(solid.Ws)",
        "intLN(u^2)", "intLN(v^2)", "intLN(w^2)"
    });
    model.result().numerical("gevSum").set("looplevelinput", new String[]{"all"});
    try {
      model.result().table().remove("tblSum");
    } catch (Exception ex) { /* ignore */ }
    model.result().table().create("tblSum", "Table");
    model.result().numerical("gevSum").set("table", "tblSum");
    model.result().numerical("gevSum").setResult();
    model.result().table("tblSum").save(OUT + "\\idt3d_sus_modes_summary.csv");
    println("WROTE idt3d_sus_modes_summary.csv");
  }

  static void exportMode(Model model, int mode1, String ds, double freqHz) throws Exception {
    String tag = "dataM" + mode1;
    try {
      model.result().export().remove(tag);
    } catch (Exception ex) { /* ignore */ }
    model.result().export().create(tag, "Data");
    model.result().export(tag).set("data", ds);
    model.result().export(tag).set("looplevelinput", new String[]{"manual"});
    model.result().export(tag).set("looplevel", new String[]{Integer.toString(mode1)});
    model.result().export(tag).set("expr", new String[]{
        "x", "y", "z",
        "u", "v", "w",
        "solid.Ws",
        "solid.eXX", "solid.eYY", "solid.eZZ",
        "solid.eXY", "solid.eYZ", "solid.eXZ",
        "solid.mises"
    });
    String fname = String.format(Locale.US, "idt3d_sus_mode_%02d_f%.6fGHz_field.csv", mode1, freqHz / 1e9);
    model.result().export(tag).set("filename", OUT + "\\" + fname);
    model.result().export(tag).set("header", "on");
    model.result().export(tag).set("sort", "on");
    model.result().export(tag).run();
    println("EXPORT_OK mode=" + mode1 + " file=" + fname);
  }

  public static void main(String[] args) {
    ModelUtil.initStandalone(true);
    try {
      Model model = ModelUtil.load("idt3dSus", MPH);
      String ds = dataSet(model);
      int nMode = modeCount(model);
      println("NMODES " + nMode);
      writeSummary(model, nMode, ds);

      double[][] fre = model.result().numerical("gevFreq").getReal();
      for (int m = 0; m < nMode; m++) {
        exportMode(model, m + 1, ds, fre[0][m]);
      }
      println("ALL_DONE");
    } catch (Throwable ex) {
      println("FAIL");
      ex.printStackTrace(System.out);
    }
    ModelUtil.disconnect();
  }
}
