d=open('out/data.json').read().replace('</','<\\/')
t=open('viewer_template.html').read()
open('out/st_andrews_build.html','w').write(t.replace('__DATA__',d))
