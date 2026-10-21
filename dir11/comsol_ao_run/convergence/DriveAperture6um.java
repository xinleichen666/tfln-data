import com.comsol.model.*;
import com.comsol.model.util.*;

/** 1 V harmonic piezoelectric drive of the refined 6 um suspended 3D IDT. */
public class DriveAperture6um {
  public static void main(String[] args) throws Exception {
    ModelUtil.initStandalone(true);
    Model m = ModelUtil.load("driven", "D:\\comsol_ao_run\\convergence\\Wap_6um_fine_Model.mph");
    try {
      try { m.physics("es").feature().remove("gnd1"); } catch (Exception ignored) {}
      m.physics("es").create("termDrive", "Terminal", 2);
      m.physics("es").feature("termDrive").selection().named("selGp");
      m.physics("es").feature("termDrive").set("TerminalType", "Voltage");
      m.physics("es").feature("termDrive").set("V0", "1[V]");
      m.physics("es").create("gndDrive", "Ground", 2);
      m.physics("es").feature("gndDrive").selection().named("selGn");

      m.physics("solid").feature("pzm1").create("dmpDrive", "Damping", 3);
      m.physics("solid").feature("pzm1").feature("dmpDrive").set("DampingType", "IsotropicLossFactor");
      m.physics("solid").feature("pzm1").feature("dmpDrive").set("eta_s_mat", "userdef");
      m.physics("solid").feature("pzm1").feature("dmpDrive").set("eta_s", "5e-4");

      m.component("comp1").variable().create("vPEdrive");
      m.component("comp1").variable("vPEdrive").selection().named("selLN");
      m.component("comp1").variable("vPEdrive").set("dnPE", "-(2.138^3/2)*(0.179*(solid.eXX+solid.eYY)+0.071*solid.eZZ)");
      m.component("comp1").cpl().create("maxLNdrive", "Maximum");
      m.component("comp1").cpl("maxLNdrive").selection().geom("geom1", 3);
      m.component("comp1").cpl("maxLNdrive").selection().named("selLN");

      m.study().create("stdDrive");
      m.study("stdDrive").create("freq", "Frequency");
      m.study("stdDrive").feature("freq").set("plist", "3.283779e9[Hz] 3.288720e9[Hz] 3.291194e9[Hz] 3.293668e9[Hz] 3.298609e9[Hz]");
      m.study("stdDrive").createAutoSequences("all");
      System.out.println("DRIVE_SOLVE_START");
      m.study("stdDrive").run();
      System.out.println("DRIVE_SOLVE_DONE");

      String[] ds = m.result().dataset().tags();
      String data = ds[ds.length - 1];
      m.result().numerical().create("gevDrive", "EvalGlobal");
      m.result().numerical("gevDrive").set("data", data);
      m.result().numerical("gevDrive").set("looplevelinput", new String[]{"all"});
      m.result().numerical("gevDrive").set("expr", new String[]{
        "freq", "maxLNdrive(sqrt(u^2+v^2+w^2))", "maxLNdrive(abs(dnPE))",
        "real(intLN(dnPE))/intLN(1)", "imag(intLN(dnPE))/intLN(1)",
        "real(intLN(solid.eXX))/intLN(1)", "imag(intLN(solid.eXX))/intLN(1)",
        "real(intLN(solid.eYY))/intLN(1)", "imag(intLN(solid.eYY))/intLN(1)",
        "real(intLN(solid.eZZ))/intLN(1)", "imag(intLN(solid.eZZ))/intLN(1)"
      });
      double[][] re = m.result().numerical("gevDrive").getReal();
      double[][] im = m.result().numerical("gevDrive").getImag();
      for (int j=0; j<re[0].length; j++) {
        System.out.printf(java.util.Locale.US,
          "ROW f_GHz=%.9f umax_nm_per_V=%.6f dnPEmax=%.9e dnPEmean_re=%.9e dnPEmean_im=%.9e eXXmean_re=%.9e eXXmean_im=%.9e eYYmean_re=%.9e eYYmean_im=%.9e eZZmean_re=%.9e eZZmean_im=%.9e%n",
          re[0][j]/1e9, re[1][j]*1e9, re[2][j], re[3][j], im[3][j], re[5][j], im[5][j], re[7][j], im[7][j], re[9][j], im[9][j]);
      }
      m.result().table().create("tblDrive", "Table");
      m.result().numerical("gevDrive").set("table", "tblDrive");
      m.result().numerical("gevDrive").setResult();
      m.result().table("tblDrive").save("D:\\comsol_ao_run\\convergence\\Wap_6um_fine_driven_1V.csv");
      m.save("D:\\comsol_ao_run\\convergence\\Wap_6um_fine_driven_Model.mph");
    } catch (Throwable t) {
      t.printStackTrace(System.out);
    } finally {
      ModelUtil.disconnect();
    }
  }
}
