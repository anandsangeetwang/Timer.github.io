import sys, json, numpy as np, trimesh, fast_simplification
sys.path.insert(0,'/home/claude/anat'); from parts import P
names = dict(l.rstrip('\n').split('\t',1) for l in open('bp/assets/BodyParts3D_data/parts_list_e.txt') if '\t' in l)
ribs = json.load(open('ribs.json'))
RIB_ZH = {'first':1,'second':2,'third':3,'fourth':4,'fifth':5,'sixth':6,'seventh':7,'eighth':8,'ninth':9,'tenth':10,'eleventh':11,'twelfth':12}
items = list(P)
for i,n in ribs.items():
    k = RIB_ZH[n.split()[1]]; items.append((i, f'第 {k} 肋骨', '胸廓'))
TARGET = {'頭骨':2500,'頸椎':1400,'胸椎':1200,'腰椎':1500,'骨盆':3500,'胸廓':700,'肩帶':2200}
scene = trimesh.Scene(); meta = []
allv = []
for i, zh, grp in items:
    m = trimesh.load(f'bp/assets/BodyParts3D_data/stl/{i}.stl', force='mesh')
    tgt = TARGET.get(grp, 2200)
    if len(m.faces) > tgt:
        v, f = fast_simplification.simplify(m.vertices.astype(np.float32), m.faces.astype(np.int32), target_reduction=1 - tgt / len(m.faces))
        m = trimesh.Trimesh(v, f, process=True)
    # BodyParts3D: mm, z up  ->  metres, y up (x right, y up, z towards viewer)
    v = m.vertices.copy() / 1000.0
    m.vertices = np.c_[v[:,0], v[:,2], -v[:,1]]
    m.fix_normals()
    en = names.get(i, i); side = 'R' if en.startswith('right') or ' right ' in en else 'L' if en.startswith('left') or ' left ' in en else ''
    zh2 = ('右' if side=='R' else '左' if side=='L' else '') + zh
    scene.add_geometry(m, node_name=i, geom_name=i)
    meta.append({'id': i, 'zh': zh2, 'en': en, 'g': grp, 'bone': grp in TARGET, 'tris': len(m.faces)})
    allv.append(m.vertices)
V = np.vstack(allv); c = (V.min(0) + V.max(0)) / 2
scene.apply_translation(-c)
open('anat/spine-shoulder.glb','wb').write(trimesh.exchange.gltf.export_glb(scene, include_normals=True))
json.dump({'parts': meta, 'bbox': (V.max(0)-V.min(0)).tolist()}, open('anat/parts.json','w'), ensure_ascii=False)
print(len(meta), sum(x['tris'] for x in meta))
