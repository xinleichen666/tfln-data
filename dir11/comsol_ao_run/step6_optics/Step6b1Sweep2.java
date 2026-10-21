import com.comsol.model.*;
import com.comsol.model.util.*;
import java.io.*;
import java.util.Locale;

public class Step6b1Sweep2 {
  static final String MPH = "D:\\comsol_ao_run\\step6_optics\\step6_solved.mph";
  static final String OUT = "D:\\comsol_ao_run\\step6_optics\\sweep_step6b1.csv";
  static final double P = 2.8526131500e-6, NB = 114, DX = P / NB, LAM = 1.55e-6;
  static final double CA = 2.843433566e6, CMB = 6.636700497e5;
  static final String PRE = "-(5.404259965)";
  static final String E2 = "cos(4.1182443e6[1/m]*(y-hLn/2))^2";
  static final String[] DN = {
    PRE + "*(0.090*solid.eYY+(-0.026)*solid.eXX+0.133*solid.eZZ)",
    PRE + "*((0.075)*(-2*solid.eXZ))",
    PRE + "*(3.4e-12[m/V]*(-es.Ex))"
  };
  static final String[] ITEM = {"PE", "PE14", "EO22", "MB"};
  static final double[] WUM = {0.8, 1.0};
  static final int[] J0 = {55, 38};
  static final int[] MB = {32, 40};

  public static void main(String[] args) {
    try {
      ModelUtil.initStandalone(true);
      System.out.println("SWEEP_START");
      Model m = ModelUtil.load("M6s2", MPH);
      String[] dts = m.result().dataset().tags();
      String ds = dts[dts.length - 1];

      int nx = 1 + 4 * WUM.length;
      String[] ex = new String[nx];
      ex[0] = "freq";
      int k = 1;
      for (int w = 0; w < WUM.length; w++) {
        String ind = "(x>=" + J0[w] + "*p/114)*(x<" + (J0[w] + MB[w]) + "*p/114)";
        for (int q = 0; q < 3; q++) {
          ex[k] = "intLN(" + DN[q] + "*" + E2 + "*" + ind + ")";
          k++;
        }
        ex[k] = "(intTop(v*" + ind + ")-intBot(v*" + ind + "))";
        k++;
      }
      System.out.println("EXPR_N " + nx);

      m.result().numerical().create("gs", "EvalGlobal");
      m.result().numerical("gs").set("data", ds);
      m.result().numerical("gs").set("expr", ex);
      m.result().numerical("gs").set("looplevelinput", new String[]{"all"});
      double[][] re = m.result().numerical("gs").getReal();
      double[][] im = m.result().numerical("gs").getImag();
      int nf = re[0].length;
      System.out.println("NF " + nf);

      StringBuilder hdr = new StringBuilder("f_GHz");
      for (int w = 0; w < WUM.length; w++) {
        for (int q = 0; q < 4; q++) {
          hdr.append(String.format(Locale.US, ",w%.1f_%s_Re,w%.1f_%s_Im", WUM[w], ITEM[q], WUM[w], ITEM[q]));
        }
        hdr.append(String.format(Locale.US, ",w%.1f_abs_tot", WUM[w]));
      }
      System.out.println("SWHDR," + hdr.toString());

      double[][] tot = new double[WUM.length][nf];
      double[] fg = new double[nf];
      for (int i = 0; i < nf; i++) {
        fg[i] = re[0][i] / 1e9;
        StringBuilder sb = new StringBuilder(String.format(Locale.US, "%.9f", fg[i]));
        for (int w = 0; w < WUM.length; w++) {
          double len = MB[w] * DX;
          double sr = 0, si = 0;
          for (int q = 0; q < 4; q++) {
            int c = 1 + 4 * w + q;
            double sc = (q == 3 ? CMB : CA) / len;
            double a = re[c][i] * sc, b = im[c][i] * sc;
            sr += a;
            si += b;
            sb.append(String.format(Locale.US, ",%.6e,%.6e", a, b));
          }
          tot[w][i] = Math.hypot(sr, si);
          sb.append(String.format(Locale.US, ",%.6e", tot[w][i]));
        }
        System.out.println("SWROW," + sb.toString());
      }

      for (int w = 0; w < WUM.length; w++) {
        int ip = 0;
        for (int i = 1; i < nf; i++) {
          if (tot[w][i] > tot[w][ip]) ip = i;
        }
        double half = tot[w][ip] / Math.sqrt(2.0);
        double fl = Double.NaN, fh = Double.NaN;
        for (int i = ip; i > 0; i--) {
          if (tot[w][i - 1] < half) {
            fl = fg[i - 1] + (half - tot[w][i - 1]) * (fg[i] - fg[i - 1]) / (tot[w][i] - tot[w][i - 1]);
            break;
          }
        }
        for (int i = ip; i < nf - 1; i++) {
          if (tot[w][i + 1] < half) {
            fh = fg[i] + (tot[w][i] - half) * (fg[i + 1] - fg[i]) / (tot[w][i] - tot[w][i + 1]);
            break;
          }
        }
        double fwhm = fh - fl;
        System.out.println(String.format(Locale.US,
          "SWEEPB1 w_um=%.1f f_peak=%.9f abs_tot_peak=%.6e f_lo=%.6f f_hi=%.6f fwhm_MHz=%.4f Q=%.1f",
          WUM[w], fg[ip], tot[w][ip], fl, fh, fwhm * 1e3, fg[ip] / fwhm));
      }

      ModelUtil.remove("M6s2");
      System.out.println("SWEEP_DONE");
    } catch (Throwable t) {
      System.out.println("SWEEP_ABORT");
      t.printStackTrace(System.out);
    }
  }
}
