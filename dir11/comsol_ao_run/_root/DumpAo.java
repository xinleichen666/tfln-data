import com.comsol.model.*;
import com.comsol.model.util.*;
import java.io.PrintWriter;

public class DumpAo {
  public static void main(String[] args) throws Exception {
    ModelUtil.initStandalone(true);
    Model model = ModelUtil.load("Model2", "D:/comsol_ao_run/ao_global_ode.mph");
    StringBuilder sb = new StringBuilder();
    try {
      sb.append("tstep ").append(model.sol("sol1").feature("t1").getString("tstepsbdf")).append("\n");
      sb.append("maxc ").append(model.sol("sol1").feature("t1").getString("maxstepconstraintbdf")).append("\n");
      sb.append("maxs ").append(model.sol("sol1").feature("t1").getString("maxstepbdf")).append("\n");
      double[] p = model.sol("sol1").getPVals();
      try {
        model.result().numerical().remove("gev1");
      } catch (Throwable ignore) {
      }
      model.result().numerical().create("gev1", "EvalGlobal");
      model.result().numerical("gev1").set("data", "dset1");
      model.result().numerical("gev1").setIndex("expr", "x1", 0);
      model.result().numerical("gev1").setIndex("expr", "y1", 1);
      model.result().numerical("gev1").setIndex("looplevelinput", "all", 0);
      double[][] real = model.result().numerical("gev1").getReal();
      sb.append("realRows ").append(real.length);
      sb.append(" realCols ").append(real[0].length);
      sb.append(" nT ").append(p.length).append("\n");
      int nRow = real.length;
      int n = real[0].length;
      for (int r = 0; r < nRow; r++) {
        sb.append("last[").append(r).append("] ").append(real[r][n - 1]).append("\n");
      }
      double sqg = Math.sqrt(2.0 * Math.PI * 0.6e9);
      double omega = 2.0 * Math.PI * 3.33e9;
      double t1 = 20e-9;
      int nq = 7;
      double[] ire = new double[nq];
      double[] iim = new double[nq];
      double[] x = real[0];
      double[] y = real[1];
      for (int i = 1; i < n; i++) {
        double tA = p[i - 1];
        double tB = p[i];
        if (tB <= t1) {
          continue;
        }
        double dt = tB - tA;
        for (int end = 0; end < 2; end++) {
          int k = end == 0 ? i - 1 : i;
          double t = p[k];
          double ar = 1.0 + sqg * x[k];
          double ai = sqg * y[k];
          double w = 0.5 * dt;
          for (int q = -3; q <= 3; q++) {
            double ang = q * omega * t;
            double c = Math.cos(ang);
            double s = Math.sin(ang);
            int iq = q + 3;
            ire[iq] += w * (ar * c - ai * s);
            iim[iq] += w * (ai * c + ar * s);
          }
        }
      }
      double tWin = p[n - 1] - t1;
      sb.append("Twindow ").append(tWin).append("\n");
      double pShift = 0;
      double pTot = 0;
      double[] pow = new double[nq];
      for (int q = -3; q <= 3; q++) {
        int iq = q + 3;
        double aRe = ire[iq] / tWin;
        double aIm = iim[iq] / tWin;
        pow[iq] = aRe * aRe + aIm * aIm;
        pTot += pow[iq];
        sb.append("q ").append(q);
        sb.append(" Ire ").append(ire[iq]);
        sb.append(" Iim ").append(iim[iq]);
        sb.append(" P ").append(pow[iq]).append("\n");
      }
      pShift = pow[4];
      sb.append("eta ").append(pShift / pTot).append("\n");
      sb.append("dBm1 ").append(10 * Math.log10(pow[2] / pShift)).append("\n");
      sb.append("dB0 ").append(10 * Math.log10(pow[3] / pShift)).append("\n");
      sb.append("dB2 ").append(10 * Math.log10(pow[5] / pShift)).append("\n");
      sb.append("dBm2 ").append(10 * Math.log10(pow[1] / pShift)).append("\n");
      sb.append("etaAbs ").append(pShift).append("\n");
      sb.append("IL ").append(-10 * Math.log10(pTot)).append("\n");
    } catch (Throwable ex) {
      sb.append("FAIL ").append(ex).append("\n");
      ex.printStackTrace();
    }
    System.out.println(sb.toString());
    model.comments(sb.toString());
    try {
      model.save("D:/comsol_ao_run/dump_probe.mph");
    } catch (Exception ex) {
      ex.printStackTrace();
    }
  }
}
