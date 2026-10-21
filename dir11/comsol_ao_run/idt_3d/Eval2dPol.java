import com.comsol.model.*;
import com.comsol.model.util.*;

public class Eval2dPol {
  public static void main(String[] args) throws Exception {
    ModelUtil.initStandalone(true);
    Model m = ModelUtil.load("Model", "D:\\comsol_ao_run\\idt_2d\\Idt2d_Model.mph");
    m.result().numerical().create("gevP", "EvalGlobal");
    m.result().numerical("gevP").set("expr", new String[]{"freq", "intLN(u^2)", "intLN(v^2)", "intLN(solid.Ws)"});
    m.result().numerical("gevP").set("looplevelinput", new String[]{"all"});
    double[][] re = m.result().numerical("gevP").getReal();
    int n = re[0].length;
    for (int i = 0; i < n; i++) {
      double f = re[0][i] / 1e9;
      double u2 = Math.abs(re[1][i]);
      double v2 = Math.abs(re[2][i]);
      double s = u2 + v2;
      System.out.println(String.format(java.util.Locale.US,
          "P2 f=%.4f pu=%.3f pv=%.3f", f, s > 0 ? u2 / s : -1, s > 0 ? v2 / s : -1));
    }
  }
}
