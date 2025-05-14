def parse_allstr_arc(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    frames = []
    i = 0
    while i < len(lines):
        if lines[i].strip().startswith("Energy"):
            energy = float(lines[i].strip().split()[-1])
            i += 1
            while not lines[i].strip().startswith("PBC"):
                i += 1
            i += 1  # Skip PBC line
            atoms = []
            while not lines[i].strip().startswith("end"):
                if lines[i].strip().startswith("H") or lines[i].strip().startswith("Pd"):
                    parts = lines[i].split()
                    pos = list(map(float, parts[1:4]))
                    atoms.append(pos)
                i += 1
            frames.append({'energy': energy, 'positions': atoms})
        i += 1
    return frames


def parse_allfor_arc(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    frames = []
    i = 0
    while i < len(lines):
        if lines[i].strip().startswith("For"):
            i += 2  # Skip two header lines
            forces = []
            while i < len(lines) and lines[i].strip() != "":
                if lines[i].strip().startswith("For"):
                    break
                parts = lines[i].strip().split()
                if len(parts) == 3:
                    forces.append(list(map(float, parts)))
                i += 1
            frames.append(forces)
        else:
            i += 1
    return frames


def write_outcar(frames_str, frames_for, output_path):
    stress_block = """  FORCE on cell =-STRESS in cart. coord.  units (eV):
  Direction    XX          YY          ZZ          XY          YZ          ZX
  --------------------------------------------------------------------------------------
  Alpha Z   298.02544   298.02544   298.02544
  Ewald  177866.49851177847.36875************    -8.31195     1.46315    -3.85925
  Hartree181790.08961181790.27974************    -3.65745    -0.44000    -0.38074
  E(xc)   -1071.12601 -1071.39406 -1074.89159    -0.05158     0.05776    -0.03247
  Local  ************************365866.27796    10.20220     0.87667     2.89802
  n-local   -72.78798   -71.94424   -96.06013     0.06837    -1.29760    -0.07144
  augment  1478.54031  1478.99491  1495.18004    -0.01742     0.78135     0.12311
  Kinetic  2782.13009  2790.47201  2812.58416     1.52447    -1.98583     1.22756
  Fock        0.00000     0.00000     0.00000     0.00000     0.00000     0.00000
  vdW       -11.37779   -11.38310    -8.44230     0.00239     0.00439    -0.00006
  -------------------------------------------------------------------------------------
  Total      -8.71449    -8.64777    -0.17541    -0.24097    -0.54011    -0.09527
  in kB     -15.12114   -15.00537    -0.30436    -0.41812    -0.93718    -0.16531
  external pressure =      -27.84 kB  Pullay stress =       17.70 kB

  kinetic pressure (ideal gas correction) =      1.02 kB
  total pressure  =     -9.12 kB
  Total+kin.   -14.171     -13.896       0.708      -0.692      -0.570      -0.221

 VOLUME and BASIS-vectors are now :
 -----------------------------------------------------------------------------
  energy-cutoff  :      450.00
  volume of cell :      923.35
      direct lattice vectors                 reciprocal lattice vectors
     5.502300000  0.000000000  0.000000000     0.181742181  0.104928897 -0.000000000
    -2.751150000  4.765131579  0.000000000     0.000000000  0.209857794 -0.000000000
     0.000000000  0.000000000 35.216700000     0.000000000  0.000000000  0.028395619

  length of vectors
     5.502300000  5.502300000 35.216700000     0.209857794  0.209857794  0.028395619

"""
    with open(output_path, 'w') as out:
        for idx, (frame_str, frame_for) in enumerate(zip(frames_str, frames_for)):
            out.write(stress_block)  # 添加应力信息块
            out.write("POSITION                                       TOTAL-FORCE (eV/Angst)\n")
            out.write(" -----------------------------------------------------------------------------------\n")
            for pos, force in zip(frame_str['positions'], frame_for):
                out.write("{:>12.5f} {:>10.5f} {:>10.5f}     {:>12.6f} {:>12.6f} {:>12.6f}\n".format(
                    pos[0], pos[1], pos[2], force[0], force[1], force[2]
                ))
            out.write(f"\n  free  energy   TOTEN  = {frame_str['energy']: .6f} eV\n\n")


if __name__ == "__main__":
    allstr = parse_allstr_arc("allstr.arc")
    allfor = parse_allfor_arc("allfor.arc")
    assert len(allstr) == len(allfor), "帧数不匹配！"
    write_outcar(allstr, allfor, "OUTCAR_formatted")
