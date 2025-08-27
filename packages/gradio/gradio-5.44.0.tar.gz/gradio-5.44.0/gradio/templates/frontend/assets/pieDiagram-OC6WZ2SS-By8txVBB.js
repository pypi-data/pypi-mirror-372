import{p as V}from"./chunk-IUKPXING-COoOjRgm.js";import{_ as p,g as U,s as j,a as q,b as Z,q as H,p as J,l as G,c as K,E as Q,I as X,O as Y,d as tt,y as et,G as at}from"./mermaid.core-CNj7h5WH.js";import{p as rt}from"./mermaid-parser.core-uaDusFyW.js";import{d as N}from"./arc-DDvSd2ZT.js";import{o as nt}from"./ordinal-BeghXfj9.js";import{b as S,t as z,n as it}from"./step-DAd4wD5P.js";import"./index-CTJ1Vjpg.js";import"./svelte/svelte.js";import"./i18n-MXuKRJOR.js";import"./dispatch-kxCwF96_.js";import"./select-BigU4G0v.js";import"./_baseUniq-BLZs-ttu.js";import"./_basePickBy-sThe3z7-.js";import"./clone-BC3wlH7y.js";import"./init-Dmth1JHB.js";function ot(t,a){return a<t?-1:a>t?1:a>=t?0:NaN}function st(t){return t}function lt(){var t=st,a=ot,m=null,o=S(0),u=S(z),x=S(0);function i(e){var r,l=(e=it(e)).length,d,A,h=0,c=new Array(l),n=new Array(l),v=+o.apply(this,arguments),w=Math.min(z,Math.max(-z,u.apply(this,arguments)-v)),f,T=Math.min(Math.abs(w)/l,x.apply(this,arguments)),$=T*(w<0?-1:1),g;for(r=0;r<l;++r)(g=n[c[r]=r]=+t(e[r],r,e))>0&&(h+=g);for(a!=null?c.sort(function(y,C){return a(n[y],n[C])}):m!=null&&c.sort(function(y,C){return m(e[y],e[C])}),r=0,A=h?(w-l*$)/h:0;r<l;++r,v=f)d=c[r],g=n[d],f=v+(g>0?g*A:0)+$,n[d]={data:e[d],index:r,value:g,startAngle:v,endAngle:f,padAngle:T};return n}return i.value=function(e){return arguments.length?(t=typeof e=="function"?e:S(+e),i):t},i.sortValues=function(e){return arguments.length?(a=e,m=null,i):a},i.sort=function(e){return arguments.length?(m=e,a=null,i):m},i.startAngle=function(e){return arguments.length?(o=typeof e=="function"?e:S(+e),i):o},i.endAngle=function(e){return arguments.length?(u=typeof e=="function"?e:S(+e),i):u},i.padAngle=function(e){return arguments.length?(x=typeof e=="function"?e:S(+e),i):x},i}var ct=at.pie,F={sections:new Map,showData:!1},k=F.sections,O=F.showData,pt=structuredClone(ct),ut=p(()=>structuredClone(pt),"getConfig"),dt=p(()=>{k=new Map,O=F.showData,et()},"clear"),gt=p(({label:t,value:a})=>{k.has(t)||(k.set(t,a),G.debug(`added new section: ${t}, with value: ${a}`))},"addSection"),ft=p(()=>k,"getSections"),mt=p(t=>{O=t},"setShowData"),ht=p(()=>O,"getShowData"),P={getConfig:ut,clear:dt,setDiagramTitle:J,getDiagramTitle:H,setAccTitle:Z,getAccTitle:q,setAccDescription:j,getAccDescription:U,addSection:gt,getSections:ft,setShowData:mt,getShowData:ht},vt=p((t,a)=>{V(t,a),a.setShowData(t.showData),t.sections.map(a.addSection)},"populateDb"),yt={parse:p(async t=>{const a=await rt("pie",t);G.debug(a),vt(a,P)},"parse")},St=p(t=>`
  .pieCircle{
    stroke: ${t.pieStrokeColor};
    stroke-width : ${t.pieStrokeWidth};
    opacity : ${t.pieOpacity};
  }
  .pieOuterCircle{
    stroke: ${t.pieOuterStrokeColor};
    stroke-width: ${t.pieOuterStrokeWidth};
    fill: none;
  }
  .pieTitleText {
    text-anchor: middle;
    font-size: ${t.pieTitleTextSize};
    fill: ${t.pieTitleTextColor};
    font-family: ${t.fontFamily};
  }
  .slice {
    font-family: ${t.fontFamily};
    fill: ${t.pieSectionTextColor};
    font-size:${t.pieSectionTextSize};
    // fill: white;
  }
  .legend text {
    fill: ${t.pieLegendTextColor};
    font-family: ${t.fontFamily};
    font-size: ${t.pieLegendTextSize};
  }
`,"getStyles"),xt=St,At=p(t=>{const a=[...t.entries()].map(o=>({label:o[0],value:o[1]})).sort((o,u)=>u.value-o.value);return lt().value(o=>o.value)(a)},"createPieArcs"),wt=p((t,a,m,o)=>{G.debug(`rendering pie chart
`+t);const u=o.db,x=K(),i=Q(u.getConfig(),x.pie),e=40,r=18,l=4,d=450,A=d,h=X(a),c=h.append("g");c.attr("transform","translate("+A/2+","+d/2+")");const{themeVariables:n}=x;let[v]=Y(n.pieOuterStrokeWidth);v??=2;const w=i.textPosition,f=Math.min(A,d)/2-e,T=N().innerRadius(0).outerRadius(f),$=N().innerRadius(f*w).outerRadius(f*w);c.append("circle").attr("cx",0).attr("cy",0).attr("r",f+v/2).attr("class","pieOuterCircle");const g=u.getSections(),y=At(g),C=[n.pie1,n.pie2,n.pie3,n.pie4,n.pie5,n.pie6,n.pie7,n.pie8,n.pie9,n.pie10,n.pie11,n.pie12],D=nt(C);c.selectAll("mySlices").data(y).enter().append("path").attr("d",T).attr("fill",s=>D(s.data.label)).attr("class","pieCircle");let W=0;g.forEach(s=>{W+=s}),c.selectAll("mySlices").data(y).enter().append("text").text(s=>(s.data.value/W*100).toFixed(0)+"%").attr("transform",s=>"translate("+$.centroid(s)+")").style("text-anchor","middle").attr("class","slice"),c.append("text").text(u.getDiagramTitle()).attr("x",0).attr("y",-400/2).attr("class","pieTitleText");const M=c.selectAll(".legend").data(D.domain()).enter().append("g").attr("class","legend").attr("transform",(s,E)=>{const b=r+l,L=b*D.domain().length/2,_=12*r,B=E*b-L;return"translate("+_+","+B+")"});M.append("rect").attr("width",r).attr("height",r).style("fill",D).style("stroke",D),M.data(y).append("text").attr("x",r+l).attr("y",r-l).text(s=>{const{label:E,value:b}=s.data;return u.getShowData()?`${E} [${b}]`:E});const R=Math.max(...M.selectAll("text").nodes().map(s=>s?.getBoundingClientRect().width??0)),I=A+e+r+l+R;h.attr("viewBox",`0 0 ${I} ${d}`),tt(h,d,I,i.useMaxWidth)},"draw"),Ct={draw:wt},Rt={parser:yt,db:P,renderer:Ct,styles:xt};export{Rt as diagram};
//# sourceMappingURL=pieDiagram-OC6WZ2SS-By8txVBB.js.map
