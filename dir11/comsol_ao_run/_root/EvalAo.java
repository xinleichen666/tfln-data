import com.comsol.model.*;
import com.comsol.model.util.*;
import java.io.PrintWriter;

public class EvalAo {
  public static void main(String[] args) {
    ModelUtil.initStandalone(true);
    Model model = run();
    try {
      if (model != null) {
        model.save("D:/comsol_ao_run/eval_probe.mph");
      }
    } catch (Exception ex) {
      ex.printStackTrace();
    }
  }

  public static Model run() {
    Model model = null;
    StringBuilder sb = new StringBuilder();
    try {
      model = ModelUtil.load("Model2", "D:/comsol_ao_run/ao_global_ode.mph");
      String[] names = model.physics("ge").feature("ge1").getStringArray("name");
      String[] eqs = model.physics("ge").feature("ge1").getStringArray("equation");
      sb.append("N=").append(names.length).append("\n");
      for (int i = 0; i < names.length; i++) {
        sb.append("NAME ").append(i).append(" ").append(names[i]).append("\n");
        sb.append("EQ ").append(eqs[i]).append("\n");
      }
      try {
        double[] p = model.sol("sol1").getPVals();
        sb.append("PVALS ").append(p.length).append(" first ").append(p[0]).append(" last ").append(p[p.length - 1]).append("\n");
      } catch (Throwable ex) {
        sb.append("PVALS_FAIL ").append(ex).append("\n");
      }
      java.util.Map<String, Double> val = new java.util.LinkedHashMap<String, Double>();
      for (String e : names) {
        try {
          model.result().numerical().remove("gev1");
        } catch (Throwable ignore) {
        }
        model.result().numerical().create("gev1", "EvalGlobal");
        model.result().numerical("gev1").set("data", "dset1");
        model.result().numerical("gev1").setIndex("expr", e, 0);
        model.result().numerical("gev1").setIndex("looplevelinput", "last", 0);
        double[][] real = model.result().numerical("gev1").getReal();
        double v = real[0][real[0].length - 1];
        val.put(e, v);
        sb.append(e).append(" = ").append(v).append("\n");
      }
      double pm1 = val.get("m1r") * val.get("m1r") + val.get("m1i") * val.get("m1i");
      double p0 = val.get("c0r") * val.get("c0r") + val.get("c0i") * val.get("c0i");
      double p1 = val.get("c1r") * val.get("c1r") + val.get("c1i") * val.get("c1i");
      double p2 = val.get("c2r") * val.get("c2r") + val.get("c2i") * val.get("c2i");
      double eta = p1 / (pm1 + p0 + p1 + p2);
      sb.append("eta = ").append(eta).append("\n");
      sb.append("dBm1 = ").append(10 * Math.log10(pm1 / p1)).append("\n");
      sb.append("dB0 = ").append(10 * Math.log10(p0 / p1)).append("\n");
      sb.append("dB2 = ").append(10 * Math.log10(p2 / p1)).append("\n");
    } catch (Throwable ex) {
      sb.append("OUTER ").append(ex).append("\n");
    }
    if (model != null) {
      model.comments(sb.toString());
    }
    System.out.println(sb.toString());
    return model;
  }
}
