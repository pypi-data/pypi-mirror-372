var st=globalThis,rt=st.ShadowRoot&&(st.ShadyCSS===void 0||st.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,vt=Symbol(),Ht=new WeakMap,W=class{constructor(t,e,r){if(this._$cssResult$=!0,r!==vt)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o,e=this.t;if(rt&&t===void 0){let r=e!==void 0&&e.length===1;r&&(t=Ht.get(e)),t===void 0&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),r&&Ht.set(e,t))}return t}toString(){return this.cssText}},It=s=>new W(typeof s=="string"?s:s+"",void 0,vt),g=(s,...t)=>{let e=s.length===1?s[0]:t.reduce((r,o,i)=>r+(a=>{if(a._$cssResult$===!0)return a.cssText;if(typeof a=="number")return a;throw Error("Value passed to 'css' function must be a 'css' function result: "+a+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(o)+s[i+1],s[0]);return new W(e,s,vt)},Nt=(s,t)=>{if(rt)s.adoptedStyleSheets=t.map(e=>e instanceof CSSStyleSheet?e:e.styleSheet);else for(let e of t){let r=document.createElement("style"),o=st.litNonce;o!==void 0&&r.setAttribute("nonce",o),r.textContent=e.cssText,s.appendChild(r)}},gt=rt?s=>s:s=>s instanceof CSSStyleSheet?(t=>{let e="";for(let r of t.cssRules)e+=r.cssText;return It(e)})(s):s;var{is:Re,defineProperty:Be,getOwnPropertyDescriptor:He,getOwnPropertyNames:Ie,getOwnPropertySymbols:Ne,getPrototypeOf:Ue}=Object,ot=globalThis,Ut=ot.trustedTypes,De=Ut?Ut.emptyScript:"",je=ot.reactiveElementPolyfillSupport,G=(s,t)=>s,K={toAttribute(s,t){switch(t){case Boolean:s=s?De:null;break;case Object:case Array:s=s==null?s:JSON.stringify(s)}return s},fromAttribute(s,t){let e=s;switch(t){case Boolean:e=s!==null;break;case Number:e=s===null?null:Number(s);break;case Object:case Array:try{e=JSON.parse(s)}catch{e=null}}return e}},it=(s,t)=>!Re(s,t),Dt={attribute:!0,type:String,converter:K,reflect:!1,useDefault:!1,hasChanged:it};Symbol.metadata??=Symbol("metadata"),ot.litPropertyMetadata??=new WeakMap;var T=class extends HTMLElement{static addInitializer(t){this._$Ei(),(this.l??=[]).push(t)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(t,e=Dt){if(e.state&&(e.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(t)&&((e=Object.create(e)).wrapped=!0),this.elementProperties.set(t,e),!e.noAccessor){let r=Symbol(),o=this.getPropertyDescriptor(t,r,e);o!==void 0&&Be(this.prototype,t,o)}}static getPropertyDescriptor(t,e,r){let{get:o,set:i}=He(this.prototype,t)??{get(){return this[e]},set(a){this[e]=a}};return{get:o,set(a){let l=o?.call(this);i?.call(this,a),this.requestUpdate(t,l,r)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)??Dt}static _$Ei(){if(this.hasOwnProperty(G("elementProperties")))return;let t=Ue(this);t.finalize(),t.l!==void 0&&(this.l=[...t.l]),this.elementProperties=new Map(t.elementProperties)}static finalize(){if(this.hasOwnProperty(G("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(G("properties"))){let e=this.properties,r=[...Ie(e),...Ne(e)];for(let o of r)this.createProperty(o,e[o])}let t=this[Symbol.metadata];if(t!==null){let e=litPropertyMetadata.get(t);if(e!==void 0)for(let[r,o]of e)this.elementProperties.set(r,o)}this._$Eh=new Map;for(let[e,r]of this.elementProperties){let o=this._$Eu(e,r);o!==void 0&&this._$Eh.set(o,e)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(t){let e=[];if(Array.isArray(t)){let r=new Set(t.flat(1/0).reverse());for(let o of r)e.unshift(gt(o))}else t!==void 0&&e.push(gt(t));return e}static _$Eu(t,e){let r=e.attribute;return r===!1?void 0:typeof r=="string"?r:typeof t=="string"?t.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(t=>t(this))}addController(t){(this._$EO??=new Set).add(t),this.renderRoot!==void 0&&this.isConnected&&t.hostConnected?.()}removeController(t){this._$EO?.delete(t)}_$E_(){let t=new Map,e=this.constructor.elementProperties;for(let r of e.keys())this.hasOwnProperty(r)&&(t.set(r,this[r]),delete this[r]);t.size>0&&(this._$Ep=t)}createRenderRoot(){let t=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return Nt(t,this.constructor.elementStyles),t}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(t=>t.hostConnected?.())}enableUpdating(t){}disconnectedCallback(){this._$EO?.forEach(t=>t.hostDisconnected?.())}attributeChangedCallback(t,e,r){this._$AK(t,r)}_$ET(t,e){let r=this.constructor.elementProperties.get(t),o=this.constructor._$Eu(t,r);if(o!==void 0&&r.reflect===!0){let i=(r.converter?.toAttribute!==void 0?r.converter:K).toAttribute(e,r.type);this._$Em=t,i==null?this.removeAttribute(o):this.setAttribute(o,i),this._$Em=null}}_$AK(t,e){let r=this.constructor,o=r._$Eh.get(t);if(o!==void 0&&this._$Em!==o){let i=r.getPropertyOptions(o),a=typeof i.converter=="function"?{fromAttribute:i.converter}:i.converter?.fromAttribute!==void 0?i.converter:K;this._$Em=o;let l=a.fromAttribute(e,i.type);this[o]=l??this._$Ej?.get(o)??l,this._$Em=null}}requestUpdate(t,e,r){if(t!==void 0){let o=this.constructor,i=this[t];if(r??=o.getPropertyOptions(t),!((r.hasChanged??it)(i,e)||r.useDefault&&r.reflect&&i===this._$Ej?.get(t)&&!this.hasAttribute(o._$Eu(t,r))))return;this.C(t,e,r)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(t,e,{useDefault:r,reflect:o,wrapped:i},a){r&&!(this._$Ej??=new Map).has(t)&&(this._$Ej.set(t,a??e??this[t]),i!==!0||a!==void 0)||(this._$AL.has(t)||(this.hasUpdated||r||(e=void 0),this._$AL.set(t,e)),o===!0&&this._$Em!==t&&(this._$Eq??=new Set).add(t))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(e){Promise.reject(e)}let t=this.scheduleUpdate();return t!=null&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(let[o,i]of this._$Ep)this[o]=i;this._$Ep=void 0}let r=this.constructor.elementProperties;if(r.size>0)for(let[o,i]of r){let{wrapped:a}=i,l=this[o];a!==!0||this._$AL.has(o)||l===void 0||this.C(o,void 0,i,l)}}let t=!1,e=this._$AL;try{t=this.shouldUpdate(e),t?(this.willUpdate(e),this._$EO?.forEach(r=>r.hostUpdate?.()),this.update(e)):this._$EM()}catch(r){throw t=!1,this._$EM(),r}t&&this._$AE(e)}willUpdate(t){}_$AE(t){this._$EO?.forEach(e=>e.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(t){return!0}update(t){this._$Eq&&=this._$Eq.forEach(e=>this._$ET(e,this[e])),this._$EM()}updated(t){}firstUpdated(t){}};T.elementStyles=[],T.shadowRootOptions={mode:"open"},T[G("elementProperties")]=new Map,T[G("finalized")]=new Map,je?.({ReactiveElement:T}),(ot.reactiveElementVersions??=[]).push("2.1.1");var yt=globalThis,at=yt.trustedTypes,jt=at?at.createPolicy("lit-html",{createHTML:s=>s}):void 0,wt="$lit$",k=`lit$${Math.random().toFixed(9).slice(2)}$`,$t="?"+k,Ve=`<${$t}>`,H=document,Y=()=>H.createComment(""),J=s=>s===null||typeof s!="object"&&typeof s!="function",xt=Array.isArray,Kt=s=>xt(s)||typeof s?.[Symbol.iterator]=="function",_t=`[ 	
\f\r]`,Z=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,Vt=/-->/g,qt=/>/g,R=RegExp(`>|${_t}(?:([^\\s"'>=/]+)(${_t}*=${_t}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),Ft=/'/g,Wt=/"/g,Zt=/^(?:script|style|textarea|title)$/i,At=s=>(t,...e)=>({_$litType$:s,strings:t,values:e}),_=At(1),Yt=At(2),Jt=At(3),P=Symbol.for("lit-noChange"),f=Symbol.for("lit-nothing"),Gt=new WeakMap,B=H.createTreeWalker(H,129);function Qt(s,t){if(!xt(s)||!s.hasOwnProperty("raw"))throw Error("invalid template strings array");return jt!==void 0?jt.createHTML(t):t}var Xt=(s,t)=>{let e=s.length-1,r=[],o,i=t===2?"<svg>":t===3?"<math>":"",a=Z;for(let l=0;l<e;l++){let n=s[l],d,u,p=-1,x=0;for(;x<n.length&&(a.lastIndex=x,u=a.exec(n),u!==null);)x=a.lastIndex,a===Z?u[1]==="!--"?a=Vt:u[1]!==void 0?a=qt:u[2]!==void 0?(Zt.test(u[2])&&(o=RegExp("</"+u[2],"g")),a=R):u[3]!==void 0&&(a=R):a===R?u[0]===">"?(a=o??Z,p=-1):u[1]===void 0?p=-2:(p=a.lastIndex-u[2].length,d=u[1],a=u[3]===void 0?R:u[3]==='"'?Wt:Ft):a===Wt||a===Ft?a=R:a===Vt||a===qt?a=Z:(a=R,o=void 0);let S=a===R&&s[l+1].startsWith("/>")?" ":"";i+=a===Z?n+Ve:p>=0?(r.push(d),n.slice(0,p)+wt+n.slice(p)+k+S):n+k+(p===-2?l:S)}return[Qt(s,i+(s[e]||"<?>")+(t===2?"</svg>":t===3?"</math>":"")),r]},Q=class s{constructor({strings:t,_$litType$:e},r){let o;this.parts=[];let i=0,a=0,l=t.length-1,n=this.parts,[d,u]=Xt(t,e);if(this.el=s.createElement(d,r),B.currentNode=this.el.content,e===2||e===3){let p=this.el.content.firstChild;p.replaceWith(...p.childNodes)}for(;(o=B.nextNode())!==null&&n.length<l;){if(o.nodeType===1){if(o.hasAttributes())for(let p of o.getAttributeNames())if(p.endsWith(wt)){let x=u[a++],S=o.getAttribute(p).split(k),O=/([.?@])?(.*)/.exec(x);n.push({type:1,index:i,name:O[2],strings:S,ctor:O[1]==="."?nt:O[1]==="?"?ct:O[1]==="@"?dt:N}),o.removeAttribute(p)}else p.startsWith(k)&&(n.push({type:6,index:i}),o.removeAttribute(p));if(Zt.test(o.tagName)){let p=o.textContent.split(k),x=p.length-1;if(x>0){o.textContent=at?at.emptyScript:"";for(let S=0;S<x;S++)o.append(p[S],Y()),B.nextNode(),n.push({type:2,index:++i});o.append(p[x],Y())}}}else if(o.nodeType===8)if(o.data===$t)n.push({type:2,index:i});else{let p=-1;for(;(p=o.data.indexOf(k,p+1))!==-1;)n.push({type:7,index:i}),p+=k.length-1}i++}}static createElement(t,e){let r=H.createElement("template");return r.innerHTML=t,r}};function I(s,t,e=s,r){if(t===P)return t;let o=r!==void 0?e._$Co?.[r]:e._$Cl,i=J(t)?void 0:t._$litDirective$;return o?.constructor!==i&&(o?._$AO?.(!1),i===void 0?o=void 0:(o=new i(s),o._$AT(s,e,r)),r!==void 0?(e._$Co??=[])[r]=o:e._$Cl=o),o!==void 0&&(t=I(s,o._$AS(s,t.values),o,r)),t}var lt=class{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){let{el:{content:e},parts:r}=this._$AD,o=(t?.creationScope??H).importNode(e,!0);B.currentNode=o;let i=B.nextNode(),a=0,l=0,n=r[0];for(;n!==void 0;){if(a===n.index){let d;n.type===2?d=new j(i,i.nextSibling,this,t):n.type===1?d=new n.ctor(i,n.name,n.strings,this,t):n.type===6&&(d=new ht(i,this,t)),this._$AV.push(d),n=r[++l]}a!==n?.index&&(i=B.nextNode(),a++)}return B.currentNode=H,o}p(t){let e=0;for(let r of this._$AV)r!==void 0&&(r.strings!==void 0?(r._$AI(t,r,e),e+=r.strings.length-2):r._$AI(t[e])),e++}},j=class s{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(t,e,r,o){this.type=2,this._$AH=f,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=r,this.options=o,this._$Cv=o?.isConnected??!0}get parentNode(){let t=this._$AA.parentNode,e=this._$AM;return e!==void 0&&t?.nodeType===11&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=I(this,t,e),J(t)?t===f||t==null||t===""?(this._$AH!==f&&this._$AR(),this._$AH=f):t!==this._$AH&&t!==P&&this._(t):t._$litType$!==void 0?this.$(t):t.nodeType!==void 0?this.T(t):Kt(t)?this.k(t):this._(t)}O(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}T(t){this._$AH!==t&&(this._$AR(),this._$AH=this.O(t))}_(t){this._$AH!==f&&J(this._$AH)?this._$AA.nextSibling.data=t:this.T(H.createTextNode(t)),this._$AH=t}$(t){let{values:e,_$litType$:r}=t,o=typeof r=="number"?this._$AC(t):(r.el===void 0&&(r.el=Q.createElement(Qt(r.h,r.h[0]),this.options)),r);if(this._$AH?._$AD===o)this._$AH.p(e);else{let i=new lt(o,this),a=i.u(this.options);i.p(e),this.T(a),this._$AH=i}}_$AC(t){let e=Gt.get(t.strings);return e===void 0&&Gt.set(t.strings,e=new Q(t)),e}k(t){xt(this._$AH)||(this._$AH=[],this._$AR());let e=this._$AH,r,o=0;for(let i of t)o===e.length?e.push(r=new s(this.O(Y()),this.O(Y()),this,this.options)):r=e[o],r._$AI(i),o++;o<e.length&&(this._$AR(r&&r._$AB.nextSibling,o),e.length=o)}_$AR(t=this._$AA.nextSibling,e){for(this._$AP?.(!1,!0,e);t!==this._$AB;){let r=t.nextSibling;t.remove(),t=r}}setConnected(t){this._$AM===void 0&&(this._$Cv=t,this._$AP?.(t))}},N=class{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(t,e,r,o,i){this.type=1,this._$AH=f,this._$AN=void 0,this.element=t,this.name=e,this._$AM=o,this.options=i,r.length>2||r[0]!==""||r[1]!==""?(this._$AH=Array(r.length-1).fill(new String),this.strings=r):this._$AH=f}_$AI(t,e=this,r,o){let i=this.strings,a=!1;if(i===void 0)t=I(this,t,e,0),a=!J(t)||t!==this._$AH&&t!==P,a&&(this._$AH=t);else{let l=t,n,d;for(t=i[0],n=0;n<i.length-1;n++)d=I(this,l[r+n],e,n),d===P&&(d=this._$AH[n]),a||=!J(d)||d!==this._$AH[n],d===f?t=f:t!==f&&(t+=(d??"")+i[n+1]),this._$AH[n]=d}a&&!o&&this.j(t)}j(t){t===f?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,t??"")}},nt=class extends N{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===f?void 0:t}},ct=class extends N{constructor(){super(...arguments),this.type=4}j(t){this.element.toggleAttribute(this.name,!!t&&t!==f)}},dt=class extends N{constructor(t,e,r,o,i){super(t,e,r,o,i),this.type=5}_$AI(t,e=this){if((t=I(this,t,e,0)??f)===P)return;let r=this._$AH,o=t===f&&r!==f||t.capture!==r.capture||t.once!==r.once||t.passive!==r.passive,i=t!==f&&(r===f||o);o&&this.element.removeEventListener(this.name,this,r),i&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,t):this._$AH.handleEvent(t)}},ht=class{constructor(t,e,r){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=r}get _$AU(){return this._$AM._$AU}_$AI(t){I(this,t)}},te={M:wt,P:k,A:$t,C:1,L:Xt,R:lt,D:Kt,V:I,I:j,H:N,N:ct,U:dt,B:nt,F:ht},qe=yt.litHtmlPolyfillSupport;qe?.(Q,j),(yt.litHtmlVersions??=[]).push("3.3.1");var ee=(s,t,e)=>{let r=e?.renderBefore??t,o=r._$litPart$;if(o===void 0){let i=e?.renderBefore??null;r._$litPart$=o=new j(t.insertBefore(Y(),i),i,void 0,e??{})}return o._$AI(s),o};var St=globalThis,z=class extends T{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){let t=super.createRenderRoot();return this.renderOptions.renderBefore??=t.firstChild,t}update(t){let e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=ee(e,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return P}};z._$litElement$=!0,z.finalized=!0,St.litElementHydrateSupport?.({LitElement:z});var Fe=St.litElementPolyfillSupport;Fe?.({LitElement:z});(St.litElementVersions??=[]).push("4.2.1");var se=g`
  :host {
    display: inline-block;
  }

  .tab {
    display: inline-flex;
    align-items: center;
    font-family: var(--sl-font-sans);
    font-size: var(--sl-font-size-small);
    font-weight: var(--sl-font-weight-semibold);
    border-radius: var(--sl-border-radius-medium);
    color: var(--sl-color-neutral-600);
    padding: var(--sl-spacing-medium) var(--sl-spacing-large);
    white-space: nowrap;
    user-select: none;
    -webkit-user-select: none;
    cursor: pointer;
    transition:
      var(--transition-speed) box-shadow,
      var(--transition-speed) color;
  }

  .tab:hover:not(.tab--disabled) {
    color: var(--sl-color-primary-600);
  }

  :host(:focus) {
    outline: transparent;
  }

  :host(:focus-visible) {
    color: var(--sl-color-primary-600);
    outline: var(--sl-focus-ring);
    outline-offset: calc(-1 * var(--sl-focus-ring-width) - var(--sl-focus-ring-offset));
  }

  .tab.tab--active:not(.tab--disabled) {
    color: var(--sl-color-primary-600);
  }

  .tab.tab--closable {
    padding-inline-end: var(--sl-spacing-small);
  }

  .tab.tab--disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .tab__close-button {
    font-size: var(--sl-font-size-small);
    margin-inline-start: var(--sl-spacing-small);
  }

  .tab__close-button::part(base) {
    padding: var(--sl-spacing-3x-small);
  }

  @media (forced-colors: active) {
    .tab.tab--active:not(.tab--disabled) {
      outline: solid 1px transparent;
      outline-offset: -3px;
    }
  }
`;var re=g`
  :host {
    display: inline-block;
    color: var(--sl-color-neutral-600);
  }

  .icon-button {
    flex: 0 0 auto;
    display: flex;
    align-items: center;
    background: none;
    border: none;
    border-radius: var(--sl-border-radius-medium);
    font-size: inherit;
    color: inherit;
    padding: var(--sl-spacing-x-small);
    cursor: pointer;
    transition: var(--sl-transition-x-fast) color;
    -webkit-appearance: none;
  }

  .icon-button:hover:not(.icon-button--disabled),
  .icon-button:focus-visible:not(.icon-button--disabled) {
    color: var(--sl-color-primary-600);
  }

  .icon-button:active:not(.icon-button--disabled) {
    color: var(--sl-color-primary-700);
  }

  .icon-button:focus {
    outline: none;
  }

  .icon-button--disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .icon-button:focus-visible {
    outline: var(--sl-focus-ring);
    outline-offset: var(--sl-focus-ring-offset);
  }

  .icon-button__icon {
    pointer-events: none;
  }
`;var Ct="";function oe(s){Ct=s}function ie(s=""){if(!Ct){let t=[...document.getElementsByTagName("script")],e=t.find(r=>r.hasAttribute("data-shoelace"));if(e)oe(e.getAttribute("data-shoelace"));else{let r=t.find(i=>/shoelace(\.min)?\.js($|\?)/.test(i.src)||/shoelace-autoloader(\.min)?\.js($|\?)/.test(i.src)),o="";r&&(o=r.getAttribute("src")),oe(o.split("/").slice(0,-1).join("/"))}}return Ct.replace(/\/$/,"")+(s?`/${s.replace(/^\//,"")}`:"")}var We={name:"default",resolver:s=>ie(`assets/icons/${s}.svg`)},ae=We;var le={caret:`
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <polyline points="6 9 12 15 18 9"></polyline>
    </svg>
  `,check:`
    <svg part="checked-icon" class="checkbox__icon" viewBox="0 0 16 16">
      <g stroke="none" stroke-width="1" fill="none" fill-rule="evenodd" stroke-linecap="round">
        <g stroke="currentColor">
          <g transform="translate(3.428571, 3.428571)">
            <path d="M0,5.71428571 L3.42857143,9.14285714"></path>
            <path d="M9.14285714,0 L3.42857143,9.14285714"></path>
          </g>
        </g>
      </g>
    </svg>
  `,"chevron-down":`
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-chevron-down" viewBox="0 0 16 16">
      <path fill-rule="evenodd" d="M1.646 4.646a.5.5 0 0 1 .708 0L8 10.293l5.646-5.647a.5.5 0 0 1 .708.708l-6 6a.5.5 0 0 1-.708 0l-6-6a.5.5 0 0 1 0-.708z"/>
    </svg>
  `,"chevron-left":`
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-chevron-left" viewBox="0 0 16 16">
      <path fill-rule="evenodd" d="M11.354 1.646a.5.5 0 0 1 0 .708L5.707 8l5.647 5.646a.5.5 0 0 1-.708.708l-6-6a.5.5 0 0 1 0-.708l6-6a.5.5 0 0 1 .708 0z"/>
    </svg>
  `,"chevron-right":`
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-chevron-right" viewBox="0 0 16 16">
      <path fill-rule="evenodd" d="M4.646 1.646a.5.5 0 0 1 .708 0l6 6a.5.5 0 0 1 0 .708l-6 6a.5.5 0 0 1-.708-.708L10.293 8 4.646 2.354a.5.5 0 0 1 0-.708z"/>
    </svg>
  `,copy:`
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-copy" viewBox="0 0 16 16">
      <path fill-rule="evenodd" d="M4 2a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V2Zm2-1a1 1 0 0 0-1 1v8a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1H6ZM2 5a1 1 0 0 0-1 1v8a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1v-1h1v1a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h1v1H2Z"/>
    </svg>
  `,eye:`
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-eye" viewBox="0 0 16 16">
      <path d="M16 8s-3-5.5-8-5.5S0 8 0 8s3 5.5 8 5.5S16 8 16 8zM1.173 8a13.133 13.133 0 0 1 1.66-2.043C4.12 4.668 5.88 3.5 8 3.5c2.12 0 3.879 1.168 5.168 2.457A13.133 13.133 0 0 1 14.828 8c-.058.087-.122.183-.195.288-.335.48-.83 1.12-1.465 1.755C11.879 11.332 10.119 12.5 8 12.5c-2.12 0-3.879-1.168-5.168-2.457A13.134 13.134 0 0 1 1.172 8z"/>
      <path d="M8 5.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5zM4.5 8a3.5 3.5 0 1 1 7 0 3.5 3.5 0 0 1-7 0z"/>
    </svg>
  `,"eye-slash":`
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-eye-slash" viewBox="0 0 16 16">
      <path d="M13.359 11.238C15.06 9.72 16 8 16 8s-3-5.5-8-5.5a7.028 7.028 0 0 0-2.79.588l.77.771A5.944 5.944 0 0 1 8 3.5c2.12 0 3.879 1.168 5.168 2.457A13.134 13.134 0 0 1 14.828 8c-.058.087-.122.183-.195.288-.335.48-.83 1.12-1.465 1.755-.165.165-.337.328-.517.486l.708.709z"/>
      <path d="M11.297 9.176a3.5 3.5 0 0 0-4.474-4.474l.823.823a2.5 2.5 0 0 1 2.829 2.829l.822.822zm-2.943 1.299.822.822a3.5 3.5 0 0 1-4.474-4.474l.823.823a2.5 2.5 0 0 0 2.829 2.829z"/>
      <path d="M3.35 5.47c-.18.16-.353.322-.518.487A13.134 13.134 0 0 0 1.172 8l.195.288c.335.48.83 1.12 1.465 1.755C4.121 11.332 5.881 12.5 8 12.5c.716 0 1.39-.133 2.02-.36l.77.772A7.029 7.029 0 0 1 8 13.5C3 13.5 0 8 0 8s.939-1.721 2.641-3.238l.708.709zm10.296 8.884-12-12 .708-.708 12 12-.708.708z"/>
    </svg>
  `,eyedropper:`
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-eyedropper" viewBox="0 0 16 16">
      <path d="M13.354.646a1.207 1.207 0 0 0-1.708 0L8.5 3.793l-.646-.647a.5.5 0 1 0-.708.708L8.293 5l-7.147 7.146A.5.5 0 0 0 1 12.5v1.793l-.854.853a.5.5 0 1 0 .708.707L1.707 15H3.5a.5.5 0 0 0 .354-.146L11 7.707l1.146 1.147a.5.5 0 0 0 .708-.708l-.647-.646 3.147-3.146a1.207 1.207 0 0 0 0-1.708l-2-2zM2 12.707l7-7L10.293 7l-7 7H2v-1.293z"></path>
    </svg>
  `,"grip-vertical":`
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-grip-vertical" viewBox="0 0 16 16">
      <path d="M7 2a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm3 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0zM7 5a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm3 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0zM7 8a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm3 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm-3 3a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm3 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm-3 3a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm3 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0z"></path>
    </svg>
  `,indeterminate:`
    <svg part="indeterminate-icon" class="checkbox__icon" viewBox="0 0 16 16">
      <g stroke="none" stroke-width="1" fill="none" fill-rule="evenodd" stroke-linecap="round">
        <g stroke="currentColor" stroke-width="2">
          <g transform="translate(2.285714, 6.857143)">
            <path d="M10.2857143,1.14285714 L1.14285714,1.14285714"></path>
          </g>
        </g>
      </g>
    </svg>
  `,"person-fill":`
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-person-fill" viewBox="0 0 16 16">
      <path d="M3 14s-1 0-1-1 1-4 6-4 6 3 6 4-1 1-1 1H3zm5-6a3 3 0 1 0 0-6 3 3 0 0 0 0 6z"/>
    </svg>
  `,"play-fill":`
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-play-fill" viewBox="0 0 16 16">
      <path d="m11.596 8.697-6.363 3.692c-.54.313-1.233-.066-1.233-.697V4.308c0-.63.692-1.01 1.233-.696l6.363 3.692a.802.802 0 0 1 0 1.393z"></path>
    </svg>
  `,"pause-fill":`
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-pause-fill" viewBox="0 0 16 16">
      <path d="M5.5 3.5A1.5 1.5 0 0 1 7 5v6a1.5 1.5 0 0 1-3 0V5a1.5 1.5 0 0 1 1.5-1.5zm5 0A1.5 1.5 0 0 1 12 5v6a1.5 1.5 0 0 1-3 0V5a1.5 1.5 0 0 1 1.5-1.5z"></path>
    </svg>
  `,radio:`
    <svg part="checked-icon" class="radio__icon" viewBox="0 0 16 16">
      <g stroke="none" stroke-width="1" fill="none" fill-rule="evenodd">
        <g fill="currentColor">
          <circle cx="8" cy="8" r="3.42857143"></circle>
        </g>
      </g>
    </svg>
  `,"star-fill":`
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-star-fill" viewBox="0 0 16 16">
      <path d="M3.612 15.443c-.386.198-.824-.149-.746-.592l.83-4.73L.173 6.765c-.329-.314-.158-.888.283-.95l4.898-.696L7.538.792c.197-.39.73-.39.927 0l2.184 4.327 4.898.696c.441.062.612.636.282.95l-3.522 3.356.83 4.73c.078.443-.36.79-.746.592L8 13.187l-4.389 2.256z"/>
    </svg>
  `,"x-lg":`
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-x-lg" viewBox="0 0 16 16">
      <path d="M2.146 2.854a.5.5 0 1 1 .708-.708L8 7.293l5.146-5.147a.5.5 0 0 1 .708.708L8.707 8l5.147 5.146a.5.5 0 0 1-.708.708L8 8.707l-5.146 5.147a.5.5 0 0 1-.708-.708L7.293 8 2.146 2.854Z"/>
    </svg>
  `,"x-circle-fill":`
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-x-circle-fill" viewBox="0 0 16 16">
      <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM5.354 4.646a.5.5 0 1 0-.708.708L7.293 8l-2.647 2.646a.5.5 0 0 0 .708.708L8 8.707l2.646 2.647a.5.5 0 0 0 .708-.708L8.707 8l2.647-2.646a.5.5 0 0 0-.708-.708L8 7.293 5.354 4.646z"></path>
    </svg>
  `},Ge={name:"system",resolver:s=>s in le?`data:image/svg+xml,${encodeURIComponent(le[s])}`:""},ne=Ge;var Ke=[ae,ne],Et=[];function ce(s){Et.push(s)}function de(s){Et=Et.filter(t=>t!==s)}function Tt(s){return Ke.find(t=>t.name===s)}var he=g`
  :host {
    display: inline-block;
    width: 1em;
    height: 1em;
    box-sizing: content-box !important;
  }

  svg {
    display: block;
    height: 100%;
    width: 100%;
  }
`;var fe=Object.defineProperty;var Ze=Object.getOwnPropertyDescriptor;var pe=Object.getOwnPropertySymbols,Ye=Object.prototype.hasOwnProperty,Je=Object.prototype.propertyIsEnumerable;var be=s=>{throw TypeError(s)},ue=(s,t,e)=>t in s?fe(s,t,{enumerable:!0,configurable:!0,writable:!0,value:e}):s[t]=e,V=(s,t)=>{for(var e in t||(t={}))Ye.call(t,e)&&ue(s,e,t[e]);if(pe)for(var e of pe(t))Je.call(t,e)&&ue(s,e,t[e]);return s};var c=(s,t,e,r)=>{for(var o=r>1?void 0:r?Ze(t,e):t,i=s.length-1,a;i>=0;i--)(a=s[i])&&(o=(r?a(t,e,o):a(o))||o);return r&&o&&fe(t,e,o),o},me=(s,t,e)=>t.has(s)||be("Cannot "+e),ve=(s,t,e)=>(me(s,t,"read from private field"),e?e.call(s):t.get(s)),ge=(s,t,e)=>t.has(s)?be("Cannot add the same private member more than once"):t instanceof WeakSet?t.add(s):t.set(s,e),_e=(s,t,e,r)=>(me(s,t,"write to private field"),r?r.call(s,e):t.set(s,e),e);function y(s,t){let e=V({waitUntilFirstUpdate:!1},t);return(r,o)=>{let{update:i}=r,a=Array.isArray(s)?s:[s];r.update=function(l){a.forEach(n=>{let d=n;if(l.has(d)){let u=l.get(d),p=this[d];u!==p&&(!e.waitUntilFirstUpdate||this.hasUpdated)&&this[o](u,p)}}),i.call(this,l)}}}var w=g`
  :host {
    box-sizing: border-box;
  }

  :host *,
  :host *::before,
  :host *::after {
    box-sizing: inherit;
  }

  [hidden] {
    display: none !important;
  }
`;var Qe={attribute:!0,type:String,converter:K,reflect:!1,hasChanged:it},Xe=(s=Qe,t,e)=>{let{kind:r,metadata:o}=e,i=globalThis.litPropertyMetadata.get(o);if(i===void 0&&globalThis.litPropertyMetadata.set(o,i=new Map),r==="setter"&&((s=Object.create(s)).wrapped=!0),i.set(e.name,s),r==="accessor"){let{name:a}=e;return{set(l){let n=t.get.call(this);t.set.call(this,l),this.requestUpdate(a,n,s)},init(l){return l!==void 0&&this.C(a,void 0,s,l),l}}}if(r==="setter"){let{name:a}=e;return function(l){let n=this[a];t.call(this,l),this.requestUpdate(a,n,s)}}throw Error("Unsupported decorator location: "+r)};function h(s){return(t,e)=>typeof e=="object"?Xe(s,t,e):((r,o,i)=>{let a=o.hasOwnProperty(i);return o.constructor.createProperty(i,r),a?Object.getOwnPropertyDescriptor(o,i):void 0})(s,t,e)}function M(s){return h({...s,state:!0,attribute:!1})}function ye(s){return(t,e)=>{let r=typeof t=="function"?t:t[e];Object.assign(r,s)}}var U=(s,t,e)=>(e.configurable=!0,e.enumerable=!0,Reflect.decorate&&typeof t!="object"&&Object.defineProperty(s,t,e),e);function L(s,t){return(e,r,o)=>{let i=a=>a.renderRoot?.querySelector(s)??null;if(t){let{get:a,set:l}=typeof r=="object"?e:o??(()=>{let n=Symbol();return{get(){return this[n]},set(d){this[n]=d}}})();return U(e,r,{get(){let n=a.call(this);return n===void 0&&(n=i(this),(n!==null||this.hasUpdated)&&l.call(this,n)),n}})}return U(e,r,{get(){return i(this)}})}}var pt,m=class extends z{constructor(){super(),ge(this,pt,!1),this.initialReflectedProperties=new Map,Object.entries(this.constructor.dependencies).forEach(([s,t])=>{this.constructor.define(s,t)})}emit(s,t){let e=new CustomEvent(s,V({bubbles:!0,cancelable:!1,composed:!0,detail:{}},t));return this.dispatchEvent(e),e}static define(s,t=this,e={}){let r=customElements.get(s);if(!r){try{customElements.define(s,t,e)}catch{customElements.define(s,class extends t{},e)}return}let o=" (unknown version)",i=o;"version"in t&&t.version&&(o=" v"+t.version),"version"in r&&r.version&&(i=" v"+r.version),!(o&&i&&o===i)&&console.warn(`Attempted to register <${s}>${o}, but <${s}>${i} has already been registered.`)}attributeChangedCallback(s,t,e){ve(this,pt)||(this.constructor.elementProperties.forEach((r,o)=>{r.reflect&&this[o]!=null&&this.initialReflectedProperties.set(o,this[o])}),_e(this,pt,!0)),super.attributeChangedCallback(s,t,e)}willUpdate(s){super.willUpdate(s),this.initialReflectedProperties.forEach((t,e)=>{s.has(e)&&this[e]==null&&(this[e]=t)})}};pt=new WeakMap;m.version="2.20.1";m.dependencies={};c([h()],m.prototype,"dir",2);c([h()],m.prototype,"lang",2);var{I:xr}=te;var we=(s,t)=>t===void 0?s?._$litType$!==void 0:s?._$litType$===t;var X=Symbol(),ut=Symbol(),kt,Pt=new Map,C=class extends m{constructor(){super(...arguments),this.initialRender=!1,this.svg=null,this.label="",this.library="default"}async resolveIcon(s,t){var e;let r;if(t?.spriteSheet)return this.svg=_`<svg part="svg">
        <use part="use" href="${s}"></use>
      </svg>`,this.svg;try{if(r=await fetch(s,{mode:"cors"}),!r.ok)return r.status===410?X:ut}catch{return ut}try{let o=document.createElement("div");o.innerHTML=await r.text();let i=o.firstElementChild;if(((e=i?.tagName)==null?void 0:e.toLowerCase())!=="svg")return X;kt||(kt=new DOMParser);let l=kt.parseFromString(i.outerHTML,"text/html").body.querySelector("svg");return l?(l.part.add("svg"),document.adoptNode(l)):X}catch{return X}}connectedCallback(){super.connectedCallback(),ce(this)}firstUpdated(){this.initialRender=!0,this.setIcon()}disconnectedCallback(){super.disconnectedCallback(),de(this)}getIconSource(){let s=Tt(this.library);return this.name&&s?{url:s.resolver(this.name),fromLibrary:!0}:{url:this.src,fromLibrary:!1}}handleLabelChange(){typeof this.label=="string"&&this.label.length>0?(this.setAttribute("role","img"),this.setAttribute("aria-label",this.label),this.removeAttribute("aria-hidden")):(this.removeAttribute("role"),this.removeAttribute("aria-label"),this.setAttribute("aria-hidden","true"))}async setIcon(){var s;let{url:t,fromLibrary:e}=this.getIconSource(),r=e?Tt(this.library):void 0;if(!t){this.svg=null;return}let o=Pt.get(t);if(o||(o=this.resolveIcon(t,r),Pt.set(t,o)),!this.initialRender)return;let i=await o;if(i===ut&&Pt.delete(t),t===this.getIconSource().url){if(we(i)){if(this.svg=i,r){await this.updateComplete;let a=this.shadowRoot.querySelector("[part='svg']");typeof r.mutator=="function"&&a&&r.mutator(a)}return}switch(i){case ut:case X:this.svg=null,this.emit("sl-error");break;default:this.svg=i.cloneNode(!0),(s=r?.mutator)==null||s.call(r,this.svg),this.emit("sl-load")}}}render(){return this.svg}};C.styles=[w,he];c([M()],C.prototype,"svg",2);c([h({reflect:!0})],C.prototype,"name",2);c([h()],C.prototype,"src",2);c([h()],C.prototype,"label",2);c([h({reflect:!0})],C.prototype,"library",2);c([y("label")],C.prototype,"handleLabelChange",1);c([y(["name","src","library"])],C.prototype,"setIcon",1);var $e={ATTRIBUTE:1,CHILD:2,PROPERTY:3,BOOLEAN_ATTRIBUTE:4,EVENT:5,ELEMENT:6},xe=s=>(...t)=>({_$litDirective$:s,values:t}),ft=class{constructor(t){}get _$AU(){return this._$AM._$AU}_$AT(t,e,r){this._$Ct=t,this._$AM=e,this._$Ci=r}_$AS(t,e){return this.update(t,e)}update(t,e){return this.render(...e)}};var E=xe(class extends ft{constructor(s){if(super(s),s.type!==$e.ATTRIBUTE||s.name!=="class"||s.strings?.length>2)throw Error("`classMap()` can only be used in the `class` attribute and must be the only part in the attribute.")}render(s){return" "+Object.keys(s).filter(t=>s[t]).join(" ")+" "}update(s,[t]){if(this.st===void 0){this.st=new Set,s.strings!==void 0&&(this.nt=new Set(s.strings.join(" ").split(/\s/).filter(r=>r!=="")));for(let r in t)t[r]&&!this.nt?.has(r)&&this.st.add(r);return this.render(t)}let e=s.element.classList;for(let r of this.st)r in t||(e.remove(r),this.st.delete(r));for(let r in t){let o=!!t[r];o===this.st.has(r)||this.nt?.has(r)||(o?(e.add(r),this.st.add(r)):(e.remove(r),this.st.delete(r)))}return P}});var Se=Symbol.for(""),ts=s=>{if(s?.r===Se)return s?._$litStatic$};var Lt=(s,...t)=>({_$litStatic$:t.reduce((e,r,o)=>e+(i=>{if(i._$litStatic$!==void 0)return i._$litStatic$;throw Error(`Value passed to 'literal' function must be a 'literal' result: ${i}. Use 'unsafeStatic' to pass non-literal values, but
            take care to ensure page security.`)})(r)+s[o+1],s[0]),r:Se}),Ae=new Map,Ot=s=>(t,...e)=>{let r=e.length,o,i,a=[],l=[],n,d=0,u=!1;for(;d<r;){for(n=t[d];d<r&&(i=e[d],(o=ts(i))!==void 0);)n+=o+t[++d],u=!0;d!==r&&l.push(i),a.push(n),d++}if(d===r&&a.push(t[r]),u){let p=a.join("$$lit$$");(t=Ae.get(p))===void 0&&(a.raw=a,Ae.set(p,t=a)),e=l}return s(t,...e)},Ce=Ot(_),Wr=Ot(Yt),Gr=Ot(Jt);var A=s=>s??f;var v=class extends m{constructor(){super(...arguments),this.hasFocus=!1,this.label="",this.disabled=!1}handleBlur(){this.hasFocus=!1,this.emit("sl-blur")}handleFocus(){this.hasFocus=!0,this.emit("sl-focus")}handleClick(s){this.disabled&&(s.preventDefault(),s.stopPropagation())}click(){this.button.click()}focus(s){this.button.focus(s)}blur(){this.button.blur()}render(){let s=!!this.href,t=s?Lt`a`:Lt`button`;return Ce`
      <${t}
        part="base"
        class=${E({"icon-button":!0,"icon-button--disabled":!s&&this.disabled,"icon-button--focused":this.hasFocus})}
        ?disabled=${A(s?void 0:this.disabled)}
        type=${A(s?void 0:"button")}
        href=${A(s?this.href:void 0)}
        target=${A(s?this.target:void 0)}
        download=${A(s?this.download:void 0)}
        rel=${A(s&&this.target?"noreferrer noopener":void 0)}
        role=${A(s?void 0:"button")}
        aria-disabled=${this.disabled?"true":"false"}
        aria-label="${this.label}"
        tabindex=${this.disabled?"-1":"0"}
        @blur=${this.handleBlur}
        @focus=${this.handleFocus}
        @click=${this.handleClick}
      >
        <sl-icon
          class="icon-button__icon"
          name=${A(this.name)}
          library=${A(this.library)}
          src=${A(this.src)}
          aria-hidden="true"
        ></sl-icon>
      </${t}>
    `}};v.styles=[w,re];v.dependencies={"sl-icon":C};c([L(".icon-button")],v.prototype,"button",2);c([M()],v.prototype,"hasFocus",2);c([h()],v.prototype,"name",2);c([h()],v.prototype,"library",2);c([h()],v.prototype,"src",2);c([h()],v.prototype,"href",2);c([h()],v.prototype,"target",2);c([h()],v.prototype,"download",2);c([h()],v.prototype,"label",2);c([h({type:Boolean,reflect:!0})],v.prototype,"disabled",2);var zt=new Set,q=new Map,D,Mt="ltr",Rt="en",Ee=typeof MutationObserver<"u"&&typeof document<"u"&&typeof document.documentElement<"u";if(Ee){let s=new MutationObserver(Te);Mt=document.documentElement.dir||"ltr",Rt=document.documentElement.lang||navigator.language,s.observe(document.documentElement,{attributes:!0,attributeFilter:["dir","lang"]})}function tt(...s){s.map(t=>{let e=t.$code.toLowerCase();q.has(e)?q.set(e,Object.assign(Object.assign({},q.get(e)),t)):q.set(e,t),D||(D=t)}),Te()}function Te(){Ee&&(Mt=document.documentElement.dir||"ltr",Rt=document.documentElement.lang||navigator.language),[...zt.keys()].map(s=>{typeof s.requestUpdate=="function"&&s.requestUpdate()})}var bt=class{constructor(t){this.host=t,this.host.addController(this)}hostConnected(){zt.add(this.host)}hostDisconnected(){zt.delete(this.host)}dir(){return`${this.host.dir||Mt}`.toLowerCase()}lang(){return`${this.host.lang||Rt}`.toLowerCase()}getTranslationData(t){var e,r;let o=new Intl.Locale(t.replace(/_/g,"-")),i=o?.language.toLowerCase(),a=(r=(e=o?.region)===null||e===void 0?void 0:e.toLowerCase())!==null&&r!==void 0?r:"",l=q.get(`${i}-${a}`),n=q.get(i);return{locale:o,language:i,region:a,primary:l,secondary:n}}exists(t,e){var r;let{primary:o,secondary:i}=this.getTranslationData((r=e.lang)!==null&&r!==void 0?r:this.lang());return e=Object.assign({includeFallback:!1},e),!!(o&&o[t]||i&&i[t]||e.includeFallback&&D&&D[t])}term(t,...e){let{primary:r,secondary:o}=this.getTranslationData(this.lang()),i;if(r&&r[t])i=r[t];else if(o&&o[t])i=o[t];else if(D&&D[t])i=D[t];else return console.error(`No translation found for: ${String(t)}`),String(t);return typeof i=="function"?i(...e):i}date(t,e){return t=new Date(t),new Intl.DateTimeFormat(this.lang(),e).format(t)}number(t,e){return t=Number(t),isNaN(t)?"":new Intl.NumberFormat(this.lang(),e).format(t)}relativeTime(t,e,r){return new Intl.RelativeTimeFormat(this.lang(),r).format(t,e)}};var ke={$code:"en",$name:"English",$dir:"ltr",carousel:"Carousel",clearEntry:"Clear entry",close:"Close",copied:"Copied",copy:"Copy",currentValue:"Current value",error:"Error",goToSlide:(s,t)=>`Go to slide ${s} of ${t}`,hidePassword:"Hide password",loading:"Loading",nextSlide:"Next slide",numOptionsSelected:s=>s===0?"No options selected":s===1?"1 option selected":`${s} options selected`,previousSlide:"Previous slide",progress:"Progress",remove:"Remove",resize:"Resize",scrollToEnd:"Scroll to end",scrollToStart:"Scroll to start",selectAColorFromTheScreen:"Select a color from the screen",showPassword:"Show password",slideNum:s=>`Slide ${s}`,toggleColorFormat:"Toggle color format"};tt(ke);var Pe=ke;var mt=class extends bt{};tt(Pe);var es=0,$=class extends m{constructor(){super(...arguments),this.localize=new mt(this),this.attrId=++es,this.componentId=`sl-tab-${this.attrId}`,this.panel="",this.active=!1,this.closable=!1,this.disabled=!1,this.tabIndex=0}connectedCallback(){super.connectedCallback(),this.setAttribute("role","tab")}handleCloseClick(s){s.stopPropagation(),this.emit("sl-close")}handleActiveChange(){this.setAttribute("aria-selected",this.active?"true":"false")}handleDisabledChange(){this.setAttribute("aria-disabled",this.disabled?"true":"false"),this.disabled&&!this.active?this.tabIndex=-1:this.tabIndex=0}render(){return this.id=this.id.length>0?this.id:this.componentId,_`
      <div
        part="base"
        class=${E({tab:!0,"tab--active":this.active,"tab--closable":this.closable,"tab--disabled":this.disabled})}
      >
        <slot></slot>
        ${this.closable?_`
              <sl-icon-button
                part="close-button"
                exportparts="base:close-button__base"
                name="x-lg"
                library="system"
                label=${this.localize.term("close")}
                class="tab__close-button"
                @click=${this.handleCloseClick}
                tabindex="-1"
              ></sl-icon-button>
            `:""}
      </div>
    `}};$.styles=[w,se];$.dependencies={"sl-icon-button":v};c([L(".tab")],$.prototype,"tab",2);c([h({reflect:!0})],$.prototype,"panel",2);c([h({type:Boolean,reflect:!0})],$.prototype,"active",2);c([h({type:Boolean,reflect:!0})],$.prototype,"closable",2);c([h({type:Boolean,reflect:!0})],$.prototype,"disabled",2);c([h({type:Number,reflect:!0})],$.prototype,"tabIndex",2);c([y("active")],$.prototype,"handleActiveChange",1);c([y("disabled")],$.prototype,"handleDisabledChange",1);$.define("sl-tab");var Le=g`
  :host {
    --indicator-color: var(--sl-color-primary-600);
    --track-color: var(--sl-color-neutral-200);
    --track-width: 2px;

    display: block;
  }

  .tab-group {
    display: flex;
    border-radius: 0;
  }

  .tab-group__tabs {
    display: flex;
    position: relative;
  }

  .tab-group__indicator {
    position: absolute;
    transition:
      var(--sl-transition-fast) translate ease,
      var(--sl-transition-fast) width ease;
  }

  .tab-group--has-scroll-controls .tab-group__nav-container {
    position: relative;
    padding: 0 var(--sl-spacing-x-large);
  }

  .tab-group--has-scroll-controls .tab-group__scroll-button--start--hidden,
  .tab-group--has-scroll-controls .tab-group__scroll-button--end--hidden {
    visibility: hidden;
  }

  .tab-group__body {
    display: block;
    overflow: auto;
  }

  .tab-group__scroll-button {
    display: flex;
    align-items: center;
    justify-content: center;
    position: absolute;
    top: 0;
    bottom: 0;
    width: var(--sl-spacing-x-large);
  }

  .tab-group__scroll-button--start {
    left: 0;
  }

  .tab-group__scroll-button--end {
    right: 0;
  }

  .tab-group--rtl .tab-group__scroll-button--start {
    left: auto;
    right: 0;
  }

  .tab-group--rtl .tab-group__scroll-button--end {
    left: 0;
    right: auto;
  }

  /*
   * Top
   */

  .tab-group--top {
    flex-direction: column;
  }

  .tab-group--top .tab-group__nav-container {
    order: 1;
  }

  .tab-group--top .tab-group__nav {
    display: flex;
    overflow-x: auto;

    /* Hide scrollbar in Firefox */
    scrollbar-width: none;
  }

  /* Hide scrollbar in Chrome/Safari */
  .tab-group--top .tab-group__nav::-webkit-scrollbar {
    width: 0;
    height: 0;
  }

  .tab-group--top .tab-group__tabs {
    flex: 1 1 auto;
    position: relative;
    flex-direction: row;
    border-bottom: solid var(--track-width) var(--track-color);
  }

  .tab-group--top .tab-group__indicator {
    bottom: calc(-1 * var(--track-width));
    border-bottom: solid var(--track-width) var(--indicator-color);
  }

  .tab-group--top .tab-group__body {
    order: 2;
  }

  .tab-group--top ::slotted(sl-tab-panel) {
    --padding: var(--sl-spacing-medium) 0;
  }

  /*
   * Bottom
   */

  .tab-group--bottom {
    flex-direction: column;
  }

  .tab-group--bottom .tab-group__nav-container {
    order: 2;
  }

  .tab-group--bottom .tab-group__nav {
    display: flex;
    overflow-x: auto;

    /* Hide scrollbar in Firefox */
    scrollbar-width: none;
  }

  /* Hide scrollbar in Chrome/Safari */
  .tab-group--bottom .tab-group__nav::-webkit-scrollbar {
    width: 0;
    height: 0;
  }

  .tab-group--bottom .tab-group__tabs {
    flex: 1 1 auto;
    position: relative;
    flex-direction: row;
    border-top: solid var(--track-width) var(--track-color);
  }

  .tab-group--bottom .tab-group__indicator {
    top: calc(-1 * var(--track-width));
    border-top: solid var(--track-width) var(--indicator-color);
  }

  .tab-group--bottom .tab-group__body {
    order: 1;
  }

  .tab-group--bottom ::slotted(sl-tab-panel) {
    --padding: var(--sl-spacing-medium) 0;
  }

  /*
   * Start
   */

  .tab-group--start {
    flex-direction: row;
  }

  .tab-group--start .tab-group__nav-container {
    order: 1;
  }

  .tab-group--start .tab-group__tabs {
    flex: 0 0 auto;
    flex-direction: column;
    border-inline-end: solid var(--track-width) var(--track-color);
  }

  .tab-group--start .tab-group__indicator {
    right: calc(-1 * var(--track-width));
    border-right: solid var(--track-width) var(--indicator-color);
  }

  .tab-group--start.tab-group--rtl .tab-group__indicator {
    right: auto;
    left: calc(-1 * var(--track-width));
  }

  .tab-group--start .tab-group__body {
    flex: 1 1 auto;
    order: 2;
  }

  .tab-group--start ::slotted(sl-tab-panel) {
    --padding: 0 var(--sl-spacing-medium);
  }

  /*
   * End
   */

  .tab-group--end {
    flex-direction: row;
  }

  .tab-group--end .tab-group__nav-container {
    order: 2;
  }

  .tab-group--end .tab-group__tabs {
    flex: 0 0 auto;
    flex-direction: column;
    border-left: solid var(--track-width) var(--track-color);
  }

  .tab-group--end .tab-group__indicator {
    left: calc(-1 * var(--track-width));
    border-inline-start: solid var(--track-width) var(--indicator-color);
  }

  .tab-group--end.tab-group--rtl .tab-group__indicator {
    right: calc(-1 * var(--track-width));
    left: auto;
  }

  .tab-group--end .tab-group__body {
    flex: 1 1 auto;
    order: 1;
  }

  .tab-group--end ::slotted(sl-tab-panel) {
    --padding: 0 var(--sl-spacing-medium);
  }
`;var Oe=g`
  :host {
    display: contents;
  }
`;var et=class extends m{constructor(){super(...arguments),this.observedElements=[],this.disabled=!1}connectedCallback(){super.connectedCallback(),this.resizeObserver=new ResizeObserver(s=>{this.emit("sl-resize",{detail:{entries:s}})}),this.disabled||this.startObserver()}disconnectedCallback(){super.disconnectedCallback(),this.stopObserver()}handleSlotChange(){this.disabled||this.startObserver()}startObserver(){let s=this.shadowRoot.querySelector("slot");if(s!==null){let t=s.assignedElements({flatten:!0});this.observedElements.forEach(e=>this.resizeObserver.unobserve(e)),this.observedElements=[],t.forEach(e=>{this.resizeObserver.observe(e),this.observedElements.push(e)})}}stopObserver(){this.resizeObserver.disconnect()}handleDisabledChange(){this.disabled?this.stopObserver():this.startObserver()}render(){return _` <slot @slotchange=${this.handleSlotChange}></slot> `}};et.styles=[w,Oe];c([h({type:Boolean,reflect:!0})],et.prototype,"disabled",2);c([y("disabled",{waitUntilFirstUpdate:!0})],et.prototype,"handleDisabledChange",1);function ss(s,t){return{top:Math.round(s.getBoundingClientRect().top-t.getBoundingClientRect().top),left:Math.round(s.getBoundingClientRect().left-t.getBoundingClientRect().left)}}function Bt(s,t,e="vertical",r="smooth"){let o=ss(s,t),i=o.top+t.scrollTop,a=o.left+t.scrollLeft,l=t.scrollLeft,n=t.scrollLeft+t.offsetWidth,d=t.scrollTop,u=t.scrollTop+t.offsetHeight;(e==="horizontal"||e==="both")&&(a<l?t.scrollTo({left:a,behavior:r}):a+s.clientWidth>n&&t.scrollTo({left:a-t.offsetWidth+s.clientWidth,behavior:r})),(e==="vertical"||e==="both")&&(i<d?t.scrollTo({top:i,behavior:r}):i+s.clientHeight>u&&t.scrollTo({top:i-t.offsetHeight+s.clientHeight,behavior:r}))}var b=class extends m{constructor(){super(...arguments),this.tabs=[],this.focusableTabs=[],this.panels=[],this.localize=new mt(this),this.hasScrollControls=!1,this.shouldHideScrollStartButton=!1,this.shouldHideScrollEndButton=!1,this.placement="top",this.activation="auto",this.noScrollControls=!1,this.fixedScrollControls=!1,this.scrollOffset=1}connectedCallback(){let s=Promise.all([customElements.whenDefined("sl-tab"),customElements.whenDefined("sl-tab-panel")]);super.connectedCallback(),this.resizeObserver=new ResizeObserver(()=>{this.repositionIndicator(),this.updateScrollControls()}),this.mutationObserver=new MutationObserver(t=>{let e=t.filter(({target:r})=>{if(r===this)return!0;if(r.closest("sl-tab-group")!==this)return!1;let o=r.tagName.toLowerCase();return o==="sl-tab"||o==="sl-tab-panel"});if(e.length!==0){if(e.some(r=>!["aria-labelledby","aria-controls"].includes(r.attributeName))&&setTimeout(()=>this.setAriaLabels()),e.some(r=>r.attributeName==="disabled"))this.syncTabsAndPanels();else if(e.some(r=>r.attributeName==="active")){let o=e.filter(i=>i.attributeName==="active"&&i.target.tagName.toLowerCase()==="sl-tab").map(i=>i.target).find(i=>i.active);o&&this.setActiveTab(o)}}}),this.updateComplete.then(()=>{this.syncTabsAndPanels(),this.mutationObserver.observe(this,{attributes:!0,attributeFilter:["active","disabled","name","panel"],childList:!0,subtree:!0}),this.resizeObserver.observe(this.nav),s.then(()=>{new IntersectionObserver((e,r)=>{var o;e[0].intersectionRatio>0&&(this.setAriaLabels(),this.setActiveTab((o=this.getActiveTab())!=null?o:this.tabs[0],{emitEvents:!1}),r.unobserve(e[0].target))}).observe(this.tabGroup)})})}disconnectedCallback(){var s,t;super.disconnectedCallback(),(s=this.mutationObserver)==null||s.disconnect(),this.nav&&((t=this.resizeObserver)==null||t.unobserve(this.nav))}getAllTabs(){return this.shadowRoot.querySelector('slot[name="nav"]').assignedElements()}getAllPanels(){return[...this.body.assignedElements()].filter(s=>s.tagName.toLowerCase()==="sl-tab-panel")}getActiveTab(){return this.tabs.find(s=>s.active)}handleClick(s){let e=s.target.closest("sl-tab");e?.closest("sl-tab-group")===this&&e!==null&&this.setActiveTab(e,{scrollBehavior:"smooth"})}handleKeyDown(s){let e=s.target.closest("sl-tab");if(e?.closest("sl-tab-group")===this&&(["Enter"," "].includes(s.key)&&e!==null&&(this.setActiveTab(e,{scrollBehavior:"smooth"}),s.preventDefault()),["ArrowLeft","ArrowRight","ArrowUp","ArrowDown","Home","End"].includes(s.key))){let o=this.tabs.find(l=>l.matches(":focus")),i=this.localize.dir()==="rtl",a=null;if(o?.tagName.toLowerCase()==="sl-tab"){if(s.key==="Home")a=this.focusableTabs[0];else if(s.key==="End")a=this.focusableTabs[this.focusableTabs.length-1];else if(["top","bottom"].includes(this.placement)&&s.key===(i?"ArrowRight":"ArrowLeft")||["start","end"].includes(this.placement)&&s.key==="ArrowUp"){let l=this.tabs.findIndex(n=>n===o);a=this.findNextFocusableTab(l,"backward")}else if(["top","bottom"].includes(this.placement)&&s.key===(i?"ArrowLeft":"ArrowRight")||["start","end"].includes(this.placement)&&s.key==="ArrowDown"){let l=this.tabs.findIndex(n=>n===o);a=this.findNextFocusableTab(l,"forward")}if(!a)return;a.tabIndex=0,a.focus({preventScroll:!0}),this.activation==="auto"?this.setActiveTab(a,{scrollBehavior:"smooth"}):this.tabs.forEach(l=>{l.tabIndex=l===a?0:-1}),["top","bottom"].includes(this.placement)&&Bt(a,this.nav,"horizontal"),s.preventDefault()}}}handleScrollToStart(){this.nav.scroll({left:this.localize.dir()==="rtl"?this.nav.scrollLeft+this.nav.clientWidth:this.nav.scrollLeft-this.nav.clientWidth,behavior:"smooth"})}handleScrollToEnd(){this.nav.scroll({left:this.localize.dir()==="rtl"?this.nav.scrollLeft-this.nav.clientWidth:this.nav.scrollLeft+this.nav.clientWidth,behavior:"smooth"})}setActiveTab(s,t){if(t=V({emitEvents:!0,scrollBehavior:"auto"},t),s!==this.activeTab&&!s.disabled){let e=this.activeTab;this.activeTab=s,this.tabs.forEach(r=>{r.active=r===this.activeTab,r.tabIndex=r===this.activeTab?0:-1}),this.panels.forEach(r=>{var o;return r.active=r.name===((o=this.activeTab)==null?void 0:o.panel)}),this.syncIndicator(),["top","bottom"].includes(this.placement)&&Bt(this.activeTab,this.nav,"horizontal",t.scrollBehavior),t.emitEvents&&(e&&this.emit("sl-tab-hide",{detail:{name:e.panel}}),this.emit("sl-tab-show",{detail:{name:this.activeTab.panel}}))}}setAriaLabels(){this.tabs.forEach(s=>{let t=this.panels.find(e=>e.name===s.panel);t&&(s.setAttribute("aria-controls",t.getAttribute("id")),t.setAttribute("aria-labelledby",s.getAttribute("id")))})}repositionIndicator(){let s=this.getActiveTab();if(!s)return;let t=s.clientWidth,e=s.clientHeight,r=this.localize.dir()==="rtl",o=this.getAllTabs(),a=o.slice(0,o.indexOf(s)).reduce((l,n)=>({left:l.left+n.clientWidth,top:l.top+n.clientHeight}),{left:0,top:0});switch(this.placement){case"top":case"bottom":this.indicator.style.width=`${t}px`,this.indicator.style.height="auto",this.indicator.style.translate=r?`${-1*a.left}px`:`${a.left}px`;break;case"start":case"end":this.indicator.style.width="auto",this.indicator.style.height=`${e}px`,this.indicator.style.translate=`0 ${a.top}px`;break}}syncTabsAndPanels(){this.tabs=this.getAllTabs(),this.focusableTabs=this.tabs.filter(s=>!s.disabled),this.panels=this.getAllPanels(),this.syncIndicator(),this.updateComplete.then(()=>this.updateScrollControls())}findNextFocusableTab(s,t){let e=null,r=t==="forward"?1:-1,o=s+r;for(;s<this.tabs.length;){if(e=this.tabs[o]||null,e===null){t==="forward"?e=this.focusableTabs[0]:e=this.focusableTabs[this.focusableTabs.length-1];break}if(!e.disabled)break;o+=r}return e}updateScrollButtons(){this.hasScrollControls&&!this.fixedScrollControls&&(this.shouldHideScrollStartButton=this.scrollFromStart()<=this.scrollOffset,this.shouldHideScrollEndButton=this.isScrolledToEnd())}isScrolledToEnd(){return this.scrollFromStart()+this.nav.clientWidth>=this.nav.scrollWidth-this.scrollOffset}scrollFromStart(){return this.localize.dir()==="rtl"?-this.nav.scrollLeft:this.nav.scrollLeft}updateScrollControls(){this.noScrollControls?this.hasScrollControls=!1:this.hasScrollControls=["top","bottom"].includes(this.placement)&&this.nav.scrollWidth>this.nav.clientWidth+1,this.updateScrollButtons()}syncIndicator(){this.getActiveTab()?(this.indicator.style.display="block",this.repositionIndicator()):this.indicator.style.display="none"}show(s){let t=this.tabs.find(e=>e.panel===s);t&&this.setActiveTab(t,{scrollBehavior:"smooth"})}render(){let s=this.localize.dir()==="rtl";return _`
      <div
        part="base"
        class=${E({"tab-group":!0,"tab-group--top":this.placement==="top","tab-group--bottom":this.placement==="bottom","tab-group--start":this.placement==="start","tab-group--end":this.placement==="end","tab-group--rtl":this.localize.dir()==="rtl","tab-group--has-scroll-controls":this.hasScrollControls})}
        @click=${this.handleClick}
        @keydown=${this.handleKeyDown}
      >
        <div class="tab-group__nav-container" part="nav">
          ${this.hasScrollControls?_`
                <sl-icon-button
                  part="scroll-button scroll-button--start"
                  exportparts="base:scroll-button__base"
                  class=${E({"tab-group__scroll-button":!0,"tab-group__scroll-button--start":!0,"tab-group__scroll-button--start--hidden":this.shouldHideScrollStartButton})}
                  name=${s?"chevron-right":"chevron-left"}
                  library="system"
                  tabindex="-1"
                  aria-hidden="true"
                  label=${this.localize.term("scrollToStart")}
                  @click=${this.handleScrollToStart}
                ></sl-icon-button>
              `:""}

          <div class="tab-group__nav" @scrollend=${this.updateScrollButtons}>
            <div part="tabs" class="tab-group__tabs" role="tablist">
              <div part="active-tab-indicator" class="tab-group__indicator"></div>
              <sl-resize-observer @sl-resize=${this.syncIndicator}>
                <slot name="nav" @slotchange=${this.syncTabsAndPanels}></slot>
              </sl-resize-observer>
            </div>
          </div>

          ${this.hasScrollControls?_`
                <sl-icon-button
                  part="scroll-button scroll-button--end"
                  exportparts="base:scroll-button__base"
                  class=${E({"tab-group__scroll-button":!0,"tab-group__scroll-button--end":!0,"tab-group__scroll-button--end--hidden":this.shouldHideScrollEndButton})}
                  name=${s?"chevron-left":"chevron-right"}
                  library="system"
                  tabindex="-1"
                  aria-hidden="true"
                  label=${this.localize.term("scrollToEnd")}
                  @click=${this.handleScrollToEnd}
                ></sl-icon-button>
              `:""}
        </div>

        <slot part="body" class="tab-group__body" @slotchange=${this.syncTabsAndPanels}></slot>
      </div>
    `}};b.styles=[w,Le];b.dependencies={"sl-icon-button":v,"sl-resize-observer":et};c([L(".tab-group")],b.prototype,"tabGroup",2);c([L(".tab-group__body")],b.prototype,"body",2);c([L(".tab-group__nav")],b.prototype,"nav",2);c([L(".tab-group__indicator")],b.prototype,"indicator",2);c([M()],b.prototype,"hasScrollControls",2);c([M()],b.prototype,"shouldHideScrollStartButton",2);c([M()],b.prototype,"shouldHideScrollEndButton",2);c([h()],b.prototype,"placement",2);c([h()],b.prototype,"activation",2);c([h({attribute:"no-scroll-controls",type:Boolean})],b.prototype,"noScrollControls",2);c([h({attribute:"fixed-scroll-controls",type:Boolean})],b.prototype,"fixedScrollControls",2);c([ye({passive:!0})],b.prototype,"updateScrollButtons",1);c([y("noScrollControls",{waitUntilFirstUpdate:!0})],b.prototype,"updateScrollControls",1);c([y("placement",{waitUntilFirstUpdate:!0})],b.prototype,"syncIndicator",1);b.define("sl-tab-group");var rs=(s,t)=>{let e=0;return function(...r){window.clearTimeout(e),e=window.setTimeout(()=>{s.call(this,...r)},t)}},ze=(s,t,e)=>{let r=s[t];s[t]=function(...o){r.call(this,...o),e.call(this,r,...o)}};(()=>{if(typeof window>"u")return;if(!("onscrollend"in window)){let t=new Set,e=new WeakMap,r=i=>{for(let a of i.changedTouches)t.add(a.identifier)},o=i=>{for(let a of i.changedTouches)t.delete(a.identifier)};document.addEventListener("touchstart",r,!0),document.addEventListener("touchend",o,!0),document.addEventListener("touchcancel",o,!0),ze(EventTarget.prototype,"addEventListener",function(i,a){if(a!=="scrollend")return;let l=rs(()=>{t.size?l():this.dispatchEvent(new Event("scrollend"))},100);i.call(this,"scroll",l,{passive:!0}),e.set(this,l)}),ze(EventTarget.prototype,"removeEventListener",function(i,a){if(a!=="scrollend")return;let l=e.get(this);l&&i.call(this,"scroll",l,{passive:!0})})}})();var Me=g`
  :host {
    --padding: 0;

    display: none;
  }

  :host([active]) {
    display: block;
  }

  .tab-panel {
    display: block;
    padding: var(--padding);
  }
`;var os=0,F=class extends m{constructor(){super(...arguments),this.attrId=++os,this.componentId=`sl-tab-panel-${this.attrId}`,this.name="",this.active=!1}connectedCallback(){super.connectedCallback(),this.id=this.id.length>0?this.id:this.componentId,this.setAttribute("role","tabpanel")}handleActiveChange(){this.setAttribute("aria-hidden",this.active?"false":"true")}render(){return _`
      <slot
        part="base"
        class=${E({"tab-panel":!0,"tab-panel--active":this.active})}
      ></slot>
    `}};F.styles=[w,Me];c([h({reflect:!0})],F.prototype,"name",2);c([h({type:Boolean,reflect:!0})],F.prototype,"active",2);c([y("active")],F.prototype,"handleActiveChange",1);F.define("sl-tab-panel");var is=()=>`<div class="alert alert-danger" role="alert">
  <strong>Airflow Balancer Config not found!</strong>
  <p>Please make sure you are running the Airflow Balancer with the correct configuration.</p>
</div>`,as=s=>`<sl-tab-panel name="defaults">
    <div class="airflow-balancer-defaults">
        <h2>Defaults</h2>
        <div class="form-group">
            <label for="default-username">Default Username</label>
            <input type="text" class="form-control" id="default-username" disabled value="${s.default_username||""}">
            <small class="form-text text-muted">Default username for all hosts.</small>
            <br>
            <label for="default-password-variable">Default Password Variable</label>
            <input type="text" class="form-control" id="default-password-variable" disabled value="${s.default_password_variable||""}">
            <small class="form-text text-muted">Default password variable for all hosts.</small>
            <br>
            <label for="default-password-variable-key">Default Password Variable Key</label>
            <input type="text" class="form-control" id="default-password-variable-key" disabled value="${s.default_password_variable_key||""}">
            <small class="form-text text-muted">Default password variable key for all hosts.</small>
            <br>
            <label for="default-key-file">Default Key File</label>
            <input type="text" class="form-control" id="default-key-file" disabled value="${s.default_key_file||""}">
            <small class="form-text text-muted">Default key file for all hosts.</small>
            <br>
            <label for="default-size">Default Size</label>
            <input type="number" class="form-control" id="default-size" disabled value="${s.default_size||0}">
            <small class="form-text text-muted">Default size for all hosts.</small>
        </div>
    </div>
    </sl-tab-panel>`,ls=s=>{let t=`
  <sl-tab-panel name="hosts">
    <div class="airflow-balancer-hosts">
      <h2>Hosts</h2>
      <table class="table table-striped table-bordered table-hover">
        <thead>
          <tr>
            <th>Name</th>
            <th>Username</th>
            <th>Password</th>
            <th>Password Variable</th>
            <th>Password Variable Key</th>
            <th>Key File</th>
            <th>OS</th>
            <th>Pool</th>
            <th>Size</th>
            <th>Queues</th>
            <th>Tags</th>
          </tr>
        </thead>
        <tbody>`;return s.hosts?.forEach(e=>{let r=e.name,o=e.username,i=e.password||"None",a=e.password_variable||"None",l=e.password_variable_key||"None",n=e.key_file||"None",d=e.os||"None",u=e.pool||"None",p=e.size||0,x=e.queues.map(O=>`<span class="badge badge-secondary">${O}</span>`).join(" "),S=e.tags.map(O=>`<span class="badge badge-secondary">${O}</span>`).join(" ");t+=`
          <tr>
            <td><span>${r}</span></td>
            <td><span>${o}</span></td>
            <td><span>${i}</span></td>
            <td><span>${a}</span></td>
            <td><span>${l}</span></td>
            <td><span>${n}</span></td>
            <td><span>${d}</span></td>
            <td><span>${u}</span></td>
            <td><span>${p}</span></td>
            <td>${x}</td>
            <td>${S}</td>
          </tr>
        `}),t+=`
        </tbody>
        </table>
    </div>
    </sl-tab-panel>
    `,t},ns=s=>{let t=`
  <sl-tab-panel name="ports">
    <div class="airflow-balancer-ports">
      <h2>Ports</h2>
      <table class="table table-striped table-bordered table-hover">
        <thead>
          <tr>
            <th>Name</th>
            <th>Host</th>
            <th>Port</th>
            <th>Tags</th>
          </tr>
        </thead>
        <tbody>`;return s.ports?.forEach(e=>{let r=e.name,o=e.tags.map(l=>`<span class="badge badge-secondary">${l}</span>`).join(" "),i=e.host_name||e.host.name,a=e.port;t+=`
          <tr>
            <td><span>${r}</span></td>
            <td><span>${i}</span></td>
            <td><span>${a}</span></td>
            <td>${o}</td>
          </tr>
        `}),t+=`
        </tbody>
        </table>
    </div>
    </sl-tab-panel>
    `,t};document.addEventListener("DOMContentLoaded",async()=>{let s=window.__AIRFLOW_BALANCER_CONFIG__,t=document.getElementById("airflow-balancer-root");if(s===void 0){t.innerHTML=is();return}let e=JSON.parse(s),r=`
<sl-tab-group id="tabGroup">
  <sl-tab slot="nav" panel="defaults">Defaults</sl-tab>
  <sl-tab slot="nav" panel="hosts">Hosts</sl-tab>
  <sl-tab slot="nav" panel="ports">Ports</sl-tab>
  ${as(e)}
  ${ls(e)}
  ${ns(e)}
</sl-tab-group>
  `;t.innerHTML=r;let o=window.location.href,i=document.querySelector("#tabGroup");i.addEventListener("sl-tab-show",l=>{let n=l.detail.name;history.pushState({},"",`#${n}`)});let a=()=>{let l=window.location.hash.slice(1),n=i.querySelector(`sl-tab[panel="${l}"]`);n&&i.show(n.panel)};window.addEventListener("popstate",a),o.indexOf("#")>0&&i.updateComplete.then(()=>{a()})});
/*! Bundled license information:

@lit/reactive-element/css-tag.js:
  (**
   * @license
   * Copyright 2019 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/reactive-element.js:
lit-html/lit-html.js:
lit-element/lit-element.js:
@lit/reactive-element/decorators/custom-element.js:
@lit/reactive-element/decorators/property.js:
@lit/reactive-element/decorators/state.js:
@lit/reactive-element/decorators/event-options.js:
@lit/reactive-element/decorators/base.js:
@lit/reactive-element/decorators/query.js:
@lit/reactive-element/decorators/query-all.js:
@lit/reactive-element/decorators/query-async.js:
@lit/reactive-element/decorators/query-assigned-nodes.js:
lit-html/directive.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

lit-html/is-server.js:
  (**
   * @license
   * Copyright 2022 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/decorators/query-assigned-elements.js:
  (**
   * @license
   * Copyright 2021 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

lit-html/directive-helpers.js:
lit-html/static.js:
  (**
   * @license
   * Copyright 2020 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

lit-html/directives/class-map.js:
lit-html/directives/if-defined.js:
  (**
   * @license
   * Copyright 2018 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)
*/
//# sourceMappingURL=index.js.map
