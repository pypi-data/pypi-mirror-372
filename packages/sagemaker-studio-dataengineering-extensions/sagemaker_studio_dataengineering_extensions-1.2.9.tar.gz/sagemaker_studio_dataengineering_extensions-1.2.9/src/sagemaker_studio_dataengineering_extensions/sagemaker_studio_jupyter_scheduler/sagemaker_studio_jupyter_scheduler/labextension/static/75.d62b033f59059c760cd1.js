"use strict";(self.webpackChunk_amzn_sagemaker_studio_jupyter_scheduler=self.webpackChunk_amzn_sagemaker_studio_jupyter_scheduler||[]).push([[75],{2372:(e,t,r)=>{r.r(t),r.d(t,{default:()=>yt});var n=r(6271),o=r.n(n),a=r(7363),i=r(3422);const l={ScheduleNoteBook:{MainPanel:{AdvancedOptions:{options:"Advanced Options",environmentVariables:"Environment variables",addEnvironmentvariable:"Add Variable",Key:"Key",Value:"Value",RoleArn:"Role ARN",Image:"Image",Kernel:"Kernel",securityGroup:"Security Group(s)",subnet:"Subnet(s)",s3InputFolder:"Input Folder",inputInDifferentAccount:"Input bucket is not in current account",inputInDifferentAccountLabel:"Enter input account ID",s3OutputFolder:"Output Folder",outputInDifferentAccount:"Output bucket is not in current account",outputInDifferentAccountLabel:"Enter output account ID",maxRetryAttempts:"Max retry attempts",maxRunTimeInSeconds:"Max run time (in seconds)",selectAdditionalDepency:"Select additional dependencies",efsPlaceholder:"Enter EFS file path",efsLabel:"Initialization script location (optional)",startUpScript:"Start-up script",executionEnv:"Execution enviroment",useVPC:"Use a Virtual Private Cloud (VPC) to run this job",enableNetworkIsolation:"Enable Network Isolation",enableEncryption:"Configure job encryption",enterKMSArnOrID:"Enter KMS key ID or ARN",ebsKey:"Job instance volume encryption KMS key",kmsKey:"Output encryption KMS key",Placeholders:{selectOrAdd:"select or add",No:"No",Add:"Add",NoneSelected:"None selected",SelectPrivateSubnets:"Select private subnet(s)",NoPrivateSubnets:"No private subnet(s) available",ImagePlaceHolder:"accountId.dkr.ecr.Region.amazonaws.com/repository[:tag] or [@digest]",KernelPlaceHolder:"kernel name",RolePlaceHolder:"arn:aws:iam::YourAccountID:role/YourRole",S3BucketPlaceHolder:"s3://bucket/path-to-your-data/"}},ErrorMessages:{JobEnvironment:{KernelImageExistError:"Image must be selected"},AdvancedOptions:{ImageError:"Image cannot be empty.",KernelError:"Kernel cannot be empty.",EFSFilePathError:"File path is not valid.",RoleArnLengthError:"Role ARN must have minimum length of 20 and maximum length of 2048.",RoleArnFormatError:"Role ARN is not properly formatted.",S3LengthError:"S3 Path must contain characters.",S3FormatError:"Invalid S3 Path format.",SecurityGroupMinError:"At least one Security Group must be selected when Subnet is selected.",SecurityGroupsMaxError:"Can only have a maximum of 5 Security Groups.",SecurityGroupSGError:"Security Group must start with sg-.",SecurityGroupLengthError:"Security Group must be less than 32 characters.",SecurityGroupFormatError:"Security Group has invalid format.",SubnetMinError:"At least one Subnet must be selected when Security Group is selected.",SubnetsMaxError:"Can only have maximum of 16 subnets.",SubnetLengthError:"Subnet must be less than 32 characters.",SubnetsFormatError:"One or more subnets has invalid format.",EnvironmentVariableEmptyError:"Key or Value cannot be empty.",EnvironmentVariableLengthError:"Key or Value cannot be more than 512 characters.",EnvironmentVariableFormatError:"Key or Value has invalid format.",KMSKeyError:"KMS key has invalid format.",MaxRetryAttemptsError:"Invalid max retry attempts must have a minimum value of 1 and a maximum value of 30.",MaxRunTimeInSecondsError:"Invalid max run time must have a minimum value of 1."},VPCErrors:{RequiresPrivateSubnet:"Running notebook jobs in a VPC requires the virtual network to use a private subnet.",NoPrivateSubnetsInSageMakerDomain:"There are no private subnets associated with your SageMaker Studio domain",YouMayChooseOtherSubnets:"You may choose to run the job using other private subnets associated with this VPC"}},Tooltips:{ImageTooltipText:"Enter the ECR registry path of the Docker image that contains the required Kernel & Libraries to execute the notebook. sagemaker-base-python-38 is selected by default",KernelTooltipText:"Enter the display name of kernel to execute the given notebook. This kernel should be installed in the above image.",LCCScriptTooltipText:"Select a lifecycle configuration script that will be run on image start-up.",VPCTooltip:"Configure the virtual network to run this job in a Virtual Private Cloud (VPC).",KMSTooltip:"Configure the cryptographic keys used to encrypt files in the job.",RoleArnTooltip:"Enter the IAM Role ARN with appropriate permissions needed to execute the notebook. By default Role name with prefix SagemakerJupyterScheduler is selected",SecurityGroupsTooltip:"Specify or add security group(s) of the desired VPC.",SubnetTooltip:"Specify or add Private subnet(s) of the desired VPC.",InputFolderTooltip:"Enter the S3 location to store the input artifacts like notebook and script.",OutputFolderTooltip:"Enter the S3 location to store the output artifacts.",InitialScriptTooltip:"Enter the file path of a local script to run before the notebook execution.",EnvironmentVariablesTooltip:"Enter key-value pairs that will be accessible in your notebook.",networkIsolationTooltip:"Enable network isolation.",kmsKeyTooltip:"If you want Amazon SageMaker to encrypt the output of your notebook job using your own AWS KMS encryption key instead of the default S3 service key, provide its ID or ARN",ebsKeyTooltip:"Encrypt data on the storage volume attached to the compute instance that runs the scheduled job.",LearnMore:"Learn more",MaxRetryAttempts:"Enter a minimum value of 1 and a maximum value of 30.",MaxRunTimeInSeconds:"Enter a minimum value of 1."},StudioTooltips:{ImageTooltipText:"Select available SageMaker image.",KernelTooltipText:"Select available SageMaker Kernel.",RoleArnTooltip:"Specify a role with permission to create a notebook job.",SecurityGroupsTooltip:"Specify or add security group(s) that have been created for the default VPC. For better security, we recommend that you use a private VPC.",SubnetTooltip:"Specify or add subnet(s) that have been created for the default VPC. For better security, we recommend that you use a private VPC.",InputFolderTooltip:"Enter the S3 location where the input folder it is located.",InputAccountIdTooltip:"Enter the S3 location where the input folder it is located.",OutputFolderTooltip:"Enter the S3 location where the output folder it is located.",OutputAccountIdTooltip:"Enter the S3 location where the input folder it is located.",InitialScriptTooltip:"Enter the EFS file path where a local script or a lifecycle configuration script is located."}}},ImageSelector:{label:"Image"},KernelSelector:{label:"Kernel",imageSelectorOption:{linkText:"More Info"}},Dialog:{awsCredentialsError:{title:"You’re not authenticated to your AWS account.",body:{text:["You haven’t provided AWS security keys or they expired. Authenticate to your AWS account with valid security keys before creating a notebook job.","Note that you must have an AWS account configured with a proper role to create notebook jobs. See %{schedulerInformation} for instructions."],links:{schedulerInformation:{linkString:"Notebook Scheduler information",linkHref:"https://docs.aws.amazon.com/sagemaker/latest/dg/notebook-auto-run.html"}}},buttons:{goToIamConsole:"Go to IAM console",enterKeysInTerminal:"Run `aws configure` in Terminal"}}}},s={expiredToken:"ExpiredToken",invalidClientTokenId:"InvalidClientTokenId",noCredentials:"NoCredentials"},u="terminal:create-new";var c,m=r(5185),d=r(3626),p=r(6516),v=r(1396),b=r(6247);!function(e){e.PublicInternetOnly="PublicInternetOnly",e.VpcOnly="VpcOnly"}(c||(c={}));var g,f,h=r(9849),y=r(9208),E=r(1982);!function(e){e[e.Large=0]="Large",e[e.Medium=1]="Medium",e[e.Small=2]="Small"}(g||(g={})),function(e){e.Filled="filled"}(f||(f={}));const j={[g.Large]:"var(--jp-content-line-height-3)",[g.Medium]:"var(--jp-content-line-height-2)",[g.Small]:"var(--jp-content-line-height-1-25)"},_={[g.Large]:"1em",[g.Medium]:"0.5em",[g.Small]:"0.25em"},k=e=>E.css`
  root: {
    background: 'var(--jp-input-active-background)',
    borderTopLeftRadius: 'var(--jp-border-radius)',
    borderTopRightRadius: 'var(--jp-border-radius)',
    fontSize: 'var(--jp-ui-font-size2)',
    '&.Mui-focused': {
      background: 'var(--jp-input-active-background)',
    },
    '&.Mui-disabled': {
      borderRadius: 'var(--jp-border-radius)',
      color: 'var(--text-input-font-color-disabled)',
    },
    '&.MuiInput-underline.Mui-disabled:before': {
      borderBottom: 'none',
    },
  },
  underline: {
    borderBottom: 'none',
    '&:before': {
      borderBottom: 'var(--jp-border-width) solid',
    },
    '&:after': {
      borderBottom: 'var(--jp-border-width) solid',
    },
    '&:not(.Mui-disabled):hover:before': {
      borderBottom: 'var(--jp-border-width) solid',
    },
    '&.Mui-error:hover:after': {
      borderBottom: 'var(--jp-border-width) solid',
    },
    '&.Mui-error:after': {
      borderBottom: 'var(--jp-border-width) solid',
    },
  },
  input: {
    color: 'var(--jp-ui-font-color0)',
    lineHeight: ${j[e]},
    padding: ${_[e]},
  },   
`,S=(E.css`
  root: {
    fontFamily: 'var(--jp-cell-prompt-font-family)',
    color: 'var(--jp-input-border-color)',
    marginBottom: 'var(--padding-small)',
    '&.Mui-error': {
      fontFamily: 'var(--jp-cell-prompt-font-family)',
      color: 'var(--jp-error-color1)',
    },
    '&.Mui-disabled': {
      fontFamily: 'var(--jp-cell-prompt-font-family)',
      color: 'var(--jp-error-color1)',
    },
  },
`,({classes:e,className:t,InputProps:r,FormHelperTextProps:n,size:a=g.Medium,variant:i,...l})=>{var s,u,c;const m=(0,E.cx)(E.css`
  .MuiFormHelperText-root.Mui-error::before {
    display: inline-block;
    vertical-align: middle;
    background-size: 1rem 1rem;
    height: var(--text-input-error-icon-height);
    width: var(--text-input-error-icon-width);
    background-image: var(--text-input-helper-text-alert-icon);
    background-repeat: no-repeat;
    content: ' ';
  }
`,t,null==e?void 0:e.root);return o().createElement(h.TextField,{"data-testid":"inputField",classes:{root:m,...e},variant:i,role:"textField",InputProps:{...r,classes:{root:(0,E.cx)(k(a),null===(s=null==r?void 0:r.classes)||void 0===s?void 0:s.root),input:(0,E.cx)(k(a),null===(u=null==r?void 0:r.classes)||void 0===u?void 0:u.input)}},FormHelperTextProps:{...n,classes:{root:(0,E.cx)(E.css`
    fontSize: 'var(--jp-ui-font-size0)',
    color: 'var(--text-input-helper-text)',
    '&.Mui-error': {
      color: 'var(--jp-error-color1)',
    },
    '&.Mui-disabled': {
      color: 'var(--jp-error-color1)',
    },
`,null===(c=null==n?void 0:n.classes)||void 0===c?void 0:c.root)}},...l})});var x,w=r(4129);!function(e){e.TopStart="top-start",e.Top="top",e.TopEnd="top-end",e.RightStart="right-start",e.Right="right",e.RightEnd="right-end",e.BottomStart="bottom-start",e.Bottom="bottom",e.BottomEnd="bottom-end",e.LeftStart="left-start",e.Left="left",e.LeftEnd="left-end"}(x||(x={}));const C=({children:e,classes:t,className:r,placement:n=x.Right,...a})=>{const i=(0,E.cx)(r,E.css`
  popper: {
    '& .MuiTooltip-tooltip': {
      backgroundColor: 'var(--color-light)',
      boxShadow: 'var(--tooltip-shadow)',
      color: 'var(--tooltip-text-color',
      padding: 'var(--padding-16)',
      fontSize: 'var(--font-size-0)',
    },
  },
`,null==t?void 0:t.popper);return o().createElement(w.Z,{...a,arrow:!0,classes:{popper:i,tooltip:E.css`
  tooltip: {
    '& .MuiTooltip-arrow': {
      color: 'var(--tooltip-surface)',
      '&:before': {
        boxShadow: 'var(--tooltip-shadow)',
      },
    },
  },
`},placement:n,"data-testid":"toolTip"},e)},P=E.css`
  display: flex;
  flex-direction: column;
`,M=E.css`
  display: flex;
  flex-direction: column;
`,T=E.css`
  display: inline-flex;
  svg {
    width: 0.75em;
    height: 0.75em;
    transform: translateY(-2px);
  }
`,I=E.css`
  svg {
    width: 0.75em;
    height: 0.75em;
    transform: translateY(1px);
  }
`,D=(e=!1)=>E.css`
  display: flex;
  flex-direction: column;
  ${e?"":"max-width : 500px;"}
  .MuiCheckbox-colorPrimary.Mui-checked {
    color: var(--jp-brand-color1);
  }
  .MuiButton-containedPrimary:hover {
    background-color: var(--jp-brand-color1);
  }
`,N=E.css`
  font-size: var(--jp-content-font-size1);
`,J=E.css`
  display: flex;
  justify-content: flex-start;
  align-items: center;
  gap: 0.5rem;
  svg {
    width: var(--jp-ui-font-size1);
    height: var(--jp-ui-font-size1);
    path {
      fill: var(--jp-error-color1);
    }
  }
`,V=(e=!1)=>E.css`
  color: var(--jp-color-root-light-800);
  font-weight: 400;
  font-size: var(--jp-ui-font-size1);
  line-height: var(--jp-ui-font-size1);
  margin-bottom: var(--jp-ui-font-size1);
  ${e&&"\n    &:after {\n      content: '*';\n      color: var(--jp-error-color1);\n    }\n  "}
`;var F,O;!function(e){e.External="_blank",e.Content="_self"}(F||(F={})),function(e){e.None="none",e.Hover="hover",e.Always="always"}(O||(O={}));const A=({className:e,disabled:t=!1,children:r,onClick:n,target:a=F.Content,...i})=>{const l=a===F.External,s={...i,className:(0,E.cx)(E.css`
  cursor: pointer;
  text-decoration: none;
  color: var(--jp-brand-color1);

  &:hover {
    text-decoration: none;
    color: var(--jp-brand-color1);
  }
`,e),target:a,onClick:t?void 0:n,rel:l?"noopener noreferrer":void 0};return o().createElement(h.Link,{...s,"data-testid":"link"},r)};r(78);const R=e=>"string"==typeof e&&e.length>0;var L=r(5505),$=r.n(L);function z(e){try{if(!$()(e)||0===e.length)return{kernel:null,arnEnvironment:null,version:null};const t=e.split("__SAGEMAKER_INTERNAL__"),[r,n]=t,o=n&&n.split("/"),a=o&&o[0]+"/"+o[1],i=3===o.length?o[2]:null;return{kernel:r,arnEnvironment:i?`${a}/${i}`:a,version:i}}catch(e){return{kernel:null,arnEnvironment:null,version:null}}}const K=({labelInfo:e,required:t,toolTipText:r,errorMessage:n,...a})=>o().createElement("div",{className:M},o().createElement("div",{className:T},o().createElement("label",{className:V(t)}," ",e," "),r&&!a.readOnly&&o().createElement(C,{title:r,className:I},o().createElement(y.Z,null))),o().createElement(S,{...a,error:R(n),helperText:n,InputProps:{readOnly:a.readOnly,...a.InputProps}}));r(6433),E.css`
  box-sizing: border-box;
  width: 100%;
  padding: var(--jp-padding-large);
  flex-direction: column;
  display: flex;
  color: var(--jp-ui-font-color0);
`,E.css`
  width: 100%;
  display: flex;
  flex-flow: row nowrap;
  justify-content: space-between;
  padding-bottom: var(--jp-padding-20);
  color: var(--jp-ui-font-color0);
`,E.css`
  max-width: 525px;
  color: var(--jp-ui-font-color2);
  margin-bottom: var(--jp-padding-medium);
`,E.css`
  display: block;
  margin-bottom: 0.5em;
  overflow-y: scroll;
`,E.css`
  align-items: center;
  display: inline-flex;
  margin-bottom: var(--jp-padding-16);
  margin-left: 1em;
  font-size: var(--jp-ui-font-size3);
  color: var(--jp-ui-font-color0);
`;const B=E.css`
  display: flex;
  flex-direction: column;
  font-size: 12px;
  color: var(--jp-ui-font-color0);
  padding: 10px;
  overflow-x: auto;
  overflow-y: hidden;
  gap: 20px;
`,G=(E.css`
  display: flex;
  justify-content: space-between;
`,E.css`
  display: flex;
  align-items: center;
`,E.css`
  margin-bottom: var(--jp-padding-medium);
`,E.css`
  width: 50% !important;
  text-align: center;
  height: 30px;
  font-size: 12px !important;
`,E.css`
  display: inline-flex;
  justify-content: right;
`,E.css`
  height: fit-content;
  width: 90px;
  text-align: center;
  margin-right: var(--jp-padding-medium);
`,E.css`
  position: absolute;
  right: 0%;
  bottom: 0%;
  margin-bottom: var(--jp-padding-large);
`,E.css`
  div:nth-child(2) {
    width: 98%;
  }
`,E.css`
  div:nth-child(2) {
    width: 49%;
  }
`,E.css`
  div:nth-child(2) {
    width: 150px;
  }
`,E.css`
  width: 500px;
  margin-bottom: var(--jp-size-4);
`),q=(E.css`
  display: flex;
  align-items: center;
`,E.css`
  display: flex;
  align-items: center;
`),Z=E.css`
  color: var(--jp-brand-color3);
`,H=(E.css`
  padding: 4px;
`,E.css`
  color: var(--jp-ui-font-color0);
`,E.css`
  display: flex;
  flex-direction: column;
  gap: var(--jp-ui-font-size1);
`,E.css`
  color: var(--jp-error-color1);
  padding: 12px;
`),U=(l.ScheduleNoteBook.MainPanel.ErrorMessages.VPCErrors,l.ScheduleNoteBook.MainPanel.AdvancedOptions,l.ScheduleNoteBook.MainPanel.Tooltips);o().createElement("div",null,o().createElement("span",{className:q}," ",U.VPCTooltip," "),o().createElement(A,{href:"https://docs.aws.amazon.com/sagemaker/latest/dg/create-notebook-auto-execution-advanced.html",target:F.External},o().createElement("p",{className:Z},l.ScheduleNoteBook.MainPanel.Tooltips.LearnMore)));var Y=r(9419),W=r(2679),Q=r(4085);const X=E.css`
  display: flex;
  align-items: flex-end;
  padding-right: 1em;
  gap: 20px;
`,ee=E.css`
  display: flex;
  flex-direction: column;
`,te=E.css`
  width: 170px;
`,re=(E.css`
  display: flex;
  flex-direction: column;
  margin-bottom: var(--jp-padding-large);
`,E.css`
  display: flex;
  flex-direction: column;
  gap: 16px;
`),ne=E.css`
  font-weight: 400;
  font-size: var(--jp-ui-font-size1);
  line-height: var(--jp-ui-font-size1);
`,oe=E.css`
  background-color: var(--jp-brand-color1);
  font-size: var(--jp-ui-font-size1);
  text-transform: none;
`,ae=E.css`
  display: inline-flex;
  align-items: center;
  gap: 6px;
  svg {
    width: 0.75em;
    height: 0.75em;
  }
`,ie=new RegExp("[a-zA-Z_][a-zA-Z0-9_]*"),le=new RegExp("[\\S\\s]*"),se=l.ScheduleNoteBook.MainPanel.ErrorMessages.AdvancedOptions,ue=l.ScheduleNoteBook.MainPanel.AdvancedOptions,ce=({isDisabled:e,environmentParameters:t,setEnvironmentParameters:r,index:n,formErrors:a,setFormErrors:i})=>{const l=t[n],s=e=>{const n=e.currentTarget.name,o=e.target.value,[a,i]=n.split("-"),l="envKey"===a?{key:o,value:t[i].value}:{key:t[i].key,value:o},s=[...t];s.splice(i,1,l),r(s)},u=()=>{const{key:e,value:t}=l;e.length<1||t.length<1?i({...a,environmentVariablesError:se.EnvironmentVariableEmptyError}):e.length>512||t.length>512?i({...a,environmentVariablesError:se.EnvironmentVariableLengthError}):ie.test(e)&&le.test(t)?i({...a,environmentVariablesError:""}):i({...a,environmentVariablesError:se.EnvironmentVariableFormatError})};return o().createElement("div",{className:X},o().createElement(K,{className:te,readOnly:e,name:`envKey-${n}`,labelInfo:ue.Key,value:t[n].key,onChange:s,onBlur:u}),o().createElement(K,{className:te,readOnly:e,name:`envValue-${n}`,labelInfo:ue.Value,value:t[n].value,onChange:s,onBlur:u}),o().createElement("div",null,!e&&o().createElement(Q.Z,{onClick:()=>{(e=>{const n=[...t];n.splice(e,1),r(n),i({...a,environmentVariablesError:""})})(n),i({...a,environmentVariablesError:""})},size:"large"},o().createElement(W.Z,null))))},me=l.ScheduleNoteBook.MainPanel.AdvancedOptions,de=l.ScheduleNoteBook.MainPanel.Tooltips,pe=({allFieldsDisabled:e,isButtonDisabled:t,environmentVariables:r,setEnvironmentVariables:n,formErrors:a,...i})=>{const l=!!a.environmentVariablesError,s=o().createElement("div",{className:J},o().createElement(Y.Z,{severity:"error"},a.environmentVariablesError));return o().createElement("div",{className:re},o().createElement("div",{className:ae},o().createElement("label",{className:ne},me.environmentVariables),e?null:o().createElement(C,{title:de.EnvironmentVariablesTooltip},o().createElement(y.Z,null))),e&&0===r.length?o().createElement("div",{className:ee},o().createElement(S,{InputProps:{readOnly:!0},placeholder:me.Placeholders.NoneSelected})):o().createElement(o().Fragment,null,r.map(((t,l)=>o().createElement(ce,{isDisabled:e,key:l,environmentParameters:r,setEnvironmentParameters:n,index:l,formErrors:a,...i})))),l&&o().createElement("div",null,s),!e&&o().createElement("div",null,o().createElement(h.Button,{disabled:t,className:oe,variant:"contained",color:"primary",size:"small",onClick:()=>{n([...r,{key:"",value:""}])}},me.addEnvironmentvariable)))};var ve=r(8992),be=r(7338),ge=r(1360);(0,ve.D)();const fe=new RegExp("^(https|s3)://([^/]+)/?(.*)$"),he=(new RegExp("[-0-9a-zA-Z]+"),new RegExp("^arn:aws[a-z\\-]*:iam::\\d{12}:role/?[a-zA-Z_0-9+=,.@\\-_/]+$")),ye=(new RegExp("^arn:aws:kms:\\w+(?:-\\w+)+:\\d{12}:key\\/[A-Za-z0-9]+(?:-[A-Za-z0-9]+)+$"),new RegExp("^[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12}$"),l.ScheduleNoteBook.MainPanel.ErrorMessages),Ee=ye.VPCErrors,je=e=>e.length<20||e.length>2048?ye.AdvancedOptions.RoleArnLengthError:he.test(e)?"":ye.AdvancedOptions.RoleArnFormatError,_e=e=>0===e.trim().length?ye.AdvancedOptions.S3LengthError:fe.test(e)?"":ye.AdvancedOptions.S3FormatError;var ke;!function(e){e.LocalJL="local-jupyter-lab",e.JupyterLab="jupyterlab",e.Studio="studio"}(ke||(ke={}));class Se{get isStudio(){return this.type===ke.Studio}get isLocalJL(){return this.type===ke.LocalJL}get isJupyterLab(){return this.type===ke.JupyterLab}get isStudioOrJupyterLab(){return this.isStudio||this.isJupyterLab}constructor(e){this.type=e,console.debug(`PluginEnvironment created with type: ${e}`)}}const xe=(0,n.createContext)(void 0);function we({app:e,children:t}){const[r,a]=(0,n.useState)((()=>function(e){return e.hasPlugin("@amzn/sagemaker-ui:project")?new Se(ke.Studio):e.hasPlugin("@amzn/sagemaker-jupyterlab-extensions:sessionmanagement")||e.hasPlugin("@amzn/sagemaker-studio-scheduler:scheduler")?new Se(ke.JupyterLab):new Se(ke.LocalJL)}(e))),i={pluginEnvironment:r,setPluginEnvironment:a};return o().createElement(xe.Provider,{value:i},t)}function Ce(){const e=(0,n.useContext)(xe);if(void 0===e)throw new Error("usePluginEnvironment must be used within a PluginEnvironmentProvider");return e}r(2346),r(3274),r(8102);const Pe=l.ScheduleNoteBook.MainPanel.AdvancedOptions,Me=l.ScheduleNoteBook.MainPanel.Tooltips,Te=(l.ScheduleNoteBook.MainPanel.StudioTooltips,l.ScheduleNoteBook.MainPanel.ErrorMessages,o().createElement("div",null,o().createElement("span",{className:q},Me.networkIsolationTooltip),o().createElement(A,{href:"https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateTrainingJob.html#sagemaker-CreateTrainingJob-request-EnableNetworkIsolation",target:F.External},o().createElement("p",{className:Z},Me.LearnMore))),o().createElement("div",null,o().createElement("span",{className:q},Me.kmsKeyTooltip),o().createElement(A,{href:"https://docs.aws.amazon.com/sagemaker/latest/dg/create-notebook-auto-execution-advanced.html",target:F.External},o().createElement("p",{className:Z},Me.LearnMore))),o().createElement("div",null,o().createElement("span",{className:q},Me.LCCScriptTooltipText),o().createElement(A,{href:"https://aws.amazon.com/blogs/machine-learning/customize-amazon-sagemaker-studio-using-lifecycle-configurations/",target:F.External},o().createElement("p",{className:Z},Me.LearnMore))),({isDisabled:e,formState:t,formErrors:r,environmentVariables:a,setEnvironmentVariables:i,lccOptions:l,availableSecurityGroups:s,availableSubnets:u,initialSubnets:c,initialSecurityGroups:m,isVPCDomain:d,requestClient:p,enableVPCSetting:v,userDefaultValues:b,setFormState:g,handleChange:f,handleNumberValueChange:h,setSubnets:y,setSecurityGroups:E,onSelectLCCScript:j,setFormValidationErrors:_,setEnableVPCSetting:k,setRoleArn:S})=>{const{pluginEnvironment:x}=Ce(),[w,C]=(0,n.useState)(!1),[P,M]=(0,n.useState)(!1),[T,I]=(0,n.useState)(!1),[D,N]=(0,n.useState)(!1);return o().createElement("div",{className:B},!1,!1,!e&&!1,(e||P)&&!1,!1,!e&&!1,(e||T)&&!1,!1,!e&&!1,(e||w)&&!1,d&&!e&&!1,(d&&v||e)&&!1,x.isStudioOrJupyterLab&&!1,o().createElement(pe,{isButtonDisabled:e||a.length>=48||!!r.environmentVariablesError,allFieldsDisabled:e,environmentVariables:a,setEnvironmentVariables:i,formErrors:r,setFormErrors:_}),!1,o().createElement(K,{name:"max_retry_attempts",type:"number",onChange:h,required:!0,disabled:D,readOnly:e,value:t.max_retry_attempts,placeholder:Pe.maxRetryAttempts,labelInfo:Pe.maxRetryAttempts,errorMessage:r.maxRetryAttemptsError,onBlur:e=>{const t=(e=>{const t=parseInt(e);return isNaN(t)||t<0||t>30?ye.AdvancedOptions.MaxRetryAttemptsError:""})(e.target.value);_({...r,maxRetryAttemptsError:t})},toolTipText:Me.MaxRetryAttempts}),o().createElement(K,{name:"max_run_time_in_seconds",type:"number",onChange:h,required:!0,disabled:D,readOnly:e,value:t.max_run_time_in_seconds,placeholder:Pe.maxRunTimeInSeconds,labelInfo:Pe.maxRunTimeInSeconds,errorMessage:r.maxRunTimeInSecondsError,onBlur:e=>{const t=(e=>{const t=parseInt(e);return isNaN(t)||t<0?ye.AdvancedOptions.MaxRunTimeInSecondsError:""})(e.target.value);_({...r,maxRunTimeInSecondsError:t})},toolTipText:Me.MaxRunTimeInSeconds}))}),Ie="No script",De=new Set(["sm_kernel","sm_image","sm_lcc_init_script_arn","role_arn","vpc_security_group_ids","vpc_subnets","s3_input","s3_output","sm_init_script","sm_output_kms_key","sm_volume_kms_key","max_run_time_in_seconds","max_retry_attempts","enable_network_isolation","DataZoneDomainId","DataZoneProjectId","DataZoneEndpoint","DataZoneDomainRegion","DataZoneStage","DataZoneEnvironmentId","ProjectS3Path"]),Ne=(e,t,r,n)=>{var o;if(r===i.JobsView.JobDetail||r===i.JobsView.JobDefinitionDetail){if(e)return e[n]?e[n].split(","):[]}else if(r===i.JobsView.CreateForm)return null===(o=null==t?void 0:t.find((e=>e.name===n)))||void 0===o?void 0:o.value;return[]},Je=(e,t,r,n)=>{var o;if(r===i.JobsView.JobDetail||r===i.JobsView.JobDefinitionDetail){if(e)return e[n]}else if(r===i.JobsView.CreateForm)return e&&n in e?e[n]:(null===(o=null==t?void 0:t.find((e=>e.name===n)))||void 0===o?void 0:o.value)||"";return""},Ve=(e,t,r,n)=>{if(t===i.JobsView.JobDetail||t===i.JobsView.JobDefinitionDetail){if(e)return e[n]}else if(t===i.JobsView.CreateForm&&e&&n in e)return e[n];return r},Fe=(e,t,r)=>{if(t===i.JobsView.JobDetail||t===i.JobsView.JobDefinitionDetail){if(e)return e[r]}else if(t===i.JobsView.CreateForm&&e&&r in e)return e[r];return""},Oe=({label:e,value:t,options:r,onChange:n,freeSolo:a,customListItemRender:i,renderInput:l,...s})=>{var u;const c=Object.fromEntries(r.map((e=>[e.value,e])));let m=t;return!a&&"string"==typeof t&&t in c&&(m=c[t]),o().createElement(o().Fragment,null,o().createElement(be.Z,{...s,id:`${e}-selectinput`,renderOption:(e,t,r)=>o().createElement("li",{...e},i?i(t,t.label,r.selected):t.label),componentsProps:{...s.componentsProps,popupIndicator:{...null===(u=s.componentsProps)||void 0===u?void 0:u.popupIndicator,size:"small"}},options:r,onChange:(e,t,r)=>{(t&&"string"!=typeof t||a)&&n&&n(t||"")},value:m,renderInput:l||(e=>o().createElement(ge.Z,{...e,variant:"outlined",size:"small",margin:"dense"}))}))},Ae=({label:e,required:t=!0,toolTipText:r,toolTipArea:n,errorMessage:a,...i})=>{const l=n&&o().createElement("div",null,o().createElement("span",{className:q},n.descriptionText),n.toolTipComponent);return o().createElement("div",{className:P},o().createElement("div",{className:T},o().createElement("label",{className:V(t)},e),(r||n)&&!i.readOnly&&o().createElement(C,{title:l||r||"",className:I,disableInteractive:null===n},o().createElement(y.Z,null))),o().createElement(Oe,{label:e,disableClearable:!0,...i}))},Re=E.css`
  display: flex;
  flex-direction: column;
  padding: 10px;
`,Le=E.css`
  display: flex;
  flex-direction: column;
  gap: 20px;
`,$e=E.css`
  display: flex;
  flex-direction: column;
`,ze=(E.css`
  transform: rotate(90deg);
`,E.css`
  display: flex;
  flex-flow: row nowrap;
  justify-content: space-between;
  align-items: center;
  width: 100%;
`),Ke=E.css`
  font-size: var(--jp-ui-font-size0);
  min-width: max-content;
`,Be=E.css`
  font-size: var(--jp-ui-font-size0);
  color: var(--jp-inverse-layout-color4);
  padding-right: 5px;
  text-overflow: ellipsis;
  overflow: hidden;
  white-space: nowrap;
`,Ge=E.css`
  width: 100%;
`,qe=E.css`
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  &[data-selected='true'] {
    background-image: var(--jp-check-icon);
    background-size: 15px;
    background-repeat: no-repeat;
    background-position: 100% center;
  }
  & > p {
    max-width: calc(100% - 10px);
  }
`,Ze=(e,t,r)=>o().createElement("span",{className:Ge},o().createElement("div",{className:qe,"data-selected":r},o().createElement("p",null,t||e.label)),He(e.optionMetadata&&e.optionMetadata.description)),He=e=>{if(!e)return;const t=e.match(/(((https?:\/\/)|(www\.))[^\s]+)/g);if(t){console.log("links",t);for(const r of t)e=e.replace(r," ")}const r=e.trim();return o().createElement("div",{className:ze},o().createElement("span",{className:Be},r),t&&t.map((e=>o().createElement(A,{className:Ke,key:e,href:e,target:F.External},l.KernelSelector.imageSelectorOption.linkText))))};r(9850);const Ue=["datascience-1.0","sagemaker-data-science-38","1.8.1-cpu-py36","pytorch-1.8-gpu-py36","sagemaker-sparkmagic","tensorflow-2.6-cpu-py38-ubuntu20.04-v1","tensorflow-2.6-gpu-py38-cu112-ubuntu20.04-v1","sagemaker-sparkanalytics-v1"];var Ye;async function We(e,t){if(e.endsWith(".ipynb"))try{return(await t.get(e)).content.metadata.kernelspec.name}catch(e){return""}return""}!function(e){e.Custom="customImage",e.Sagemaker="smeImage",e.Session="session"}(Ye||(Ye={}));const Qe={smeImage:"Sagemaker Image",customImage:"Custom Image",prefered:"Use image from preferred session",session:"Use image from other session"};function Xe(e,t,r){const n=Object.values(e).filter((e=>{const n=e.arnEnvironment.split("/")[1];return r?(null==e?void 0:e.group)===t&&Ue.includes(n):((null==e?void 0:e.group)!==Ye.Sagemaker||!e.label.includes("Geospatial"))&&(null==e?void 0:e.group)===t}));return{label:Qe[t],value:"",options:n.map((e=>({label:e.label,value:t===Ye.Session?e.label:e.arnEnvironment,group:Qe[t],optionMetadata:e,options:e.versionOptions})))}}const et=l.ScheduleNoteBook.MainPanel.Tooltips,tt=l.ScheduleNoteBook.MainPanel.StudioTooltips,rt=({isDisabled:e,formState:t,formErrors:r,setFormState:a,setFormErrors:s,model:u,jobsView:c,requestClient:m,contentsManager:d})=>{var p,g;const{pluginEnvironment:f}=Ce(),[h,y]=(0,n.useState)({arnEnvironment:null,kernel:null,version:null}),[E,j]=(0,n.useState)({});(0,n.useEffect)((()=>{(async function(e){const t=v.URLExt.join(e.baseUrl,"api/kernelspecs"),r=await b.ServerConnection.makeRequest(t,{},e);if(200===r.status)return await r.json()})(m).then((async e=>{var t;e&&j(function(e){const t={},r=e.kernelspecs;return Object.values(r).forEach((e=>{var r;if(!e)return;const n=(null===(r=e.spec)||void 0===r?void 0:r.metadata)?e.spec.metadata.sme_metadata:null,{imageName:o,kernelName:a}=function(e){try{if(!$()(e)||0===e.length)return{imageName:null,kernelName:null};const[t,r]=e.split("(");return{imageName:r&&r.slice(0,-1).split("/")[0],kernelName:t&&t.slice(0,-1)}}catch(e){return{imageName:null,kernelName:null}}}(e.spec.display_name),{kernel:i,arnEnvironment:l,version:s}=z(e.name);if(!(i&&l&&o&&a))return;const u={arnEnvironment:l,kernelOptions:[{label:a,value:i}],versionOptions:s?[{label:`v${s}`,value:s}]:void 0,label:s?`${o} v${s}`:o,description:(null==n?void 0:n.description)?n.description:void 0,group:n&&n.is_template?Ye.Sagemaker:Ye.Custom};if(t[l]){const{kernelOptions:e}=t[l];if(!e.some((e=>e.value===i))){const r=[...e,{label:a,value:i}];t[l].kernelOptions=r}if(s){const{versionOptions:e}=t[l];if(!e.some((e=>e.value===s))){const r={label:`v${s}`,value:s.toString()},n=Array.isArray(e)?[...e,r]:[r];t[l].versionOptions=n}}}else t[l]=u})),t}(e));const r=await We(u.inputFile,d),n=r in(null!==(t=null==e?void 0:e.kernelspecs)&&void 0!==t?t:{})?r:"",o=((e,t,r)=>{if(r===i.JobsView.JobDetail||r===i.JobsView.JobDefinitionDetail){if(e){const{sm_kernel:t,sm_image:r}=e;return z(`${t}__SAGEMAKER_INTERNAL__${r}`)}return{kernel:null,arnEnvironment:null,version:null}}if(r===i.JobsView.CreateForm){if(e&&"sm_image"in e){const{sm_kernel:t,sm_image:r}=e;return z(`${t}__SAGEMAKER_INTERNAL__${r}`)}return z(t)||{kernel:null,arnEnvironment:null,version:null}}return z(t)||{kernel:null,arnEnvironment:null,version:null}})(u.runtimeEnvironmentParameters,n,c);y(o),a((e=>({...e,sm_kernel:o.kernel||"",sm_image:o.arnEnvironment||""})))}))}),[]);const _=[...null!==(p=Xe(E,Ye.Sagemaker,!1).options)&&void 0!==p?p:[],...null!==(g=Xe(E,Ye.Custom).options)&&void 0!==g?g:[]],k=(0,n.useMemo)((()=>{var e;return h.arnEnvironment&&(null===(e=E[h.arnEnvironment])||void 0===e?void 0:e.kernelOptions)||[]}),[E,h]),S=!!r.jobEnvironmentError,x=o().createElement("div",{className:J},o().createElement(Y.Z,{severity:"error"},r.jobEnvironmentError));return(0,n.useEffect)((()=>{h.arnEnvironment&&h.kernel&&r.jobEnvironmentError&&s({...r,jobEnvironmentError:""})}),[h.arnEnvironment,h.kernel]),0===Object.keys(E).length?null:o().createElement("div",{className:Re},o().createElement("div",{className:Le},o().createElement("div",{className:$e},o().createElement(Ae,{"data-testid":"sm_image_dropdown",options:_,value:h.arnEnvironment,label:l.ImageSelector.label,customListItemRender:Ze,onChange:(e,r)=>{var n;if(!e||"string"==typeof e)return;const o=(null===(n=e.optionMetadata)||void 0===n?void 0:n.kernelOptions)||[],i=o.length>0?o[0].value:null,l=r?r.value:null;a({...t,sm_image:e.value+(l?"/"+l:""),sm_kernel:null!=i?i:""}),y({arnEnvironment:e.value,kernel:i,version:l})},readOnly:e,groupBy:e=>{var t;return null!==(t=e.group)&&void 0!==t?t:""},toolTipText:f.isStudio?tt.ImageTooltipText:et.ImageTooltipText}),r.jobEnvironmentError&&o().createElement("div",{className:N},S&&x)),o().createElement(Ae,{options:k,value:h.kernel,label:l.KernelSelector.label,onChange:e=>{e&&"string"!=typeof e&&e&&(a({...t,sm_kernel:e.value}),y({...h,kernel:e.value}))},readOnly:e,toolTipText:f.isStudio?tt.KernelTooltipText:et.KernelTooltipText})))},nt=l.ScheduleNoteBook.MainPanel.AdvancedOptions,ot=l.ScheduleNoteBook.MainPanel.Tooltips,at=({setFormState:e,formState:t,isDisabled:r,formErrors:a,setFormErrors:i,model:l,executionEnvironments:s})=>{const u=(0,n.useMemo)((()=>((e,t)=>{var r,n;if(e){const{sm_kernel:t,sm_image:r}=e;return z(`${t}__SAGEMAKER_INTERNAL__${r}`)}const o=null===(r=null==t?void 0:t.find((e=>"image"===e.name)))||void 0===r?void 0:r.value,a=null===(n=null==t?void 0:t.find((e=>"kernel"===e.name)))||void 0===n?void 0:n.value;return R(o)&&R(a)?z(`${a}__SAGEMAKER_INTERNAL__${o}`):{kernel:null,arnEnvironment:null,version:null}})(l.runtimeEnvironmentParameters,null==s?void 0:s.auto_detected_config)),[]);(0,n.useEffect)((()=>{e({...t,sm_kernel:u.kernel||"",sm_image:u.arnEnvironment||""})}),[u]);const c=r=>{const n=r.target.name,o=r.target.value;e({...t,[n]:o})};return o().createElement("div",{className:B},o().createElement(K,{name:"sm_image",onChange:c,readOnly:r,required:!0,value:t.sm_image,placeholder:nt.Placeholders.ImagePlaceHolder,labelInfo:nt.Image,errorMessage:a.ImageError,onBlur:e=>{const{value:t}=e.target,r=t.length<=0?ye.AdvancedOptions.ImageError:"";i({...a,ImageError:r})},toolTipText:ot.ImageTooltipText}),o().createElement(K,{name:"sm_kernel",onChange:c,readOnly:r,required:!0,value:t.sm_kernel,placeholder:nt.Placeholders.KernelPlaceHolder,labelInfo:nt.Kernel,errorMessage:a.KernelError,onBlur:e=>{const{value:t}=e.target,r=t.length<=0?ye.AdvancedOptions.KernelError:"";i({...a,KernelError:r})},toolTipText:ot.KernelTooltipText}))},it=l.ScheduleNoteBook.MainPanel.Tooltips,lt=({setFormState:e,formState:t,isDisabled:r,formErrors:a,setFormErrors:i,contentsManager:s,model:u})=>{const[c,m]=(0,n.useState)([]),[d,p]=(0,n.useState)([]),g=async()=>{const e=b.ServerConnection.makeSettings(),t=v.URLExt.join(e.baseUrl,"/sagemaker_studio_jupyter_scheduler/sagemaker_images"),r=await b.ServerConnection.makeRequest(t,{},e);return 200==r.status?(await r.json()).map((e=>({label:e.image_display_name,value:e.image_arn}))):[]},f=async()=>{const e=b.ServerConnection.makeSettings(),t=v.URLExt.join(e.baseUrl,"/api/kernelspecs"),r=await b.ServerConnection.makeRequest(t,{},e);let n=null;const o=[],a=[];if(200===r.status){const e=await r.json();n=e.default,e.kernelspecs&&Object.values(e.kernelspecs).forEach((e=>{if(e){o.push(e.name);let t=e.name;e.spec&&(t=e.spec.display_name),a.push({label:t,value:e.name})}}))}return{defaultKernelName:n,kernelNames:o,kernelOptions:a}};return(0,n.useEffect)((()=>{Promise.all([We(u.inputFile,s),g(),f()]).then((t=>{const r=t[0],n=t[1],o=t[2];let a,i;n&&n.length>0&&m(n),u.runtimeEnvironmentParameters&&u.runtimeEnvironmentParameters.sm_image?a=u.runtimeEnvironmentParameters.sm_image:n&&n.length>0&&(a=n[0].value),o&&o.kernelOptions&&o.kernelOptions.length>0&&p(o.kernelOptions),i=u.runtimeEnvironmentParameters&&u.runtimeEnvironmentParameters.sm_kernel?u.runtimeEnvironmentParameters.sm_kernel:o.kernelNames.indexOf(r)>=0?r:o.defaultKernelName||"",e((e=>({...e,sm_image:null!=a?a:"",sm_kernel:null!=i?i:""})))})).catch((e=>console.error(e)))}),[]),o().createElement("div",{className:B},o().createElement(Ae,{"data-testid":"sm_image_dropdown",options:c,value:t.sm_image,label:l.ImageSelector.label,onChange:r=>{r&&"string"!=typeof r&&e({...t,sm_image:r.value})},readOnly:r,toolTipText:it.ImageTooltipText,required:!0}),o().createElement(Ae,{"data-testid":"sm_kernel_dropdown",options:d,value:t.sm_kernel,label:l.KernelSelector.label,onChange:r=>{r&&"string"!=typeof r&&e({...t,sm_kernel:r.value})},readOnly:r,toolTipText:it.KernelTooltipText,required:!0}))},st=e=>{const{pluginEnvironment:t}=Ce();return o().createElement(o().Fragment,null,t.isStudio&&o().createElement(rt,{...e}),t.isJupyterLab&&o().createElement(lt,{...e}),t.isLocalJL&&o().createElement(at,{...e}))},ut=e=>{const{executionEnvironments:t,settingRegistry:r,jobsView:a,requestClient:l,errors:s,handleErrorsChange:u,model:m,handleModelChange:d}=e,p=(0,n.useMemo)((()=>{return e=null==t?void 0:t.auto_detected_config,a===i.JobsView.CreateForm&&(null===(r=null==e?void 0:e.find((e=>"app_network_access_type"===e.name)))||void 0===r?void 0:r.value)||"";var e,r}),[]),v=a===i.JobsView.JobDefinitionDetail||a===i.JobsView.JobDetail,b=(0,n.useMemo)((()=>{var e,r;const n=[],o=(null===(r=null===(e=t.auto_detected_config)||void 0===e?void 0:e.find((e=>"lcc_arn"===e.name)))||void 0===r?void 0:r.value)||[];n.push(Ie),n.push(...o);const l=(s=m.runtimeEnvironmentParameters,((u=a)===i.JobsView.JobDetail||u===i.JobsView.JobDefinitionDetail)&&s&&s.sm_lcc_init_script_arn||Ie);var s,u;return m.runtimeEnvironmentParameters&&l!==Ie&&n.push(l),{allLCCOptions:n,selectedLccValue:l}}),[]),g=(0,n.useMemo)((()=>((e,t,r)=>{var n;if(r===i.JobsView.JobDetail||r===i.JobsView.JobDefinitionDetail){if(e)return e.role_arn}else if(r===i.JobsView.CreateForm){if(e&&"role_arn"in e)return e.role_arn;const r=null===(n=null==t?void 0:t.find((e=>"role_arn"===e.name)))||void 0===n?void 0:n.value;if((null==r?void 0:r.length)>0)return r[0]}return""})(m.runtimeEnvironmentParameters,t.auto_detected_config,a)),[]),f=(0,n.useMemo)((()=>Je(m.runtimeEnvironmentParameters,t.auto_detected_config,a,"s3_output")),[]),h=(0,n.useMemo)((()=>Je(m.runtimeEnvironmentParameters,t.auto_detected_config,a,"s3_input")),[]),y=(0,n.useMemo)((()=>Ve(m.runtimeEnvironmentParameters,a,1,"max_retry_attempts")),[]),E=(0,n.useMemo)((()=>((e,t,r)=>{if(t===i.JobsView.JobDetail||t===i.JobsView.JobDefinitionDetail){if(e)return Boolean(e[r])}else if(t===i.JobsView.CreateForm&&e&&r in e)return Boolean(e[r]);return!1})(m.runtimeEnvironmentParameters,a,"enable_network_isolation")),[]),j=(0,n.useMemo)((()=>Ve(m.runtimeEnvironmentParameters,a,172800,"max_run_time_in_seconds")),[]),_=(0,n.useMemo)((()=>{var e,r;const n=(null===(r=null===(e=t.auto_detected_config)||void 0===e?void 0:e.find((e=>"vpc_security_group_ids"===e.name)))||void 0===r?void 0:r.value)||[];return null==n?void 0:n.map((e=>e.name))}),[]),k=(0,n.useMemo)((()=>{var e,r;const n=(null===(r=null===(e=t.auto_detected_config)||void 0===e?void 0:e.find((e=>"vpc_subnets"===e.name)))||void 0===r?void 0:r.value)||[];return null==n?void 0:n.map((e=>e.name))}),[]),S=(0,n.useMemo)((()=>p===c.PublicInternetOnly?{securityGroups:[],subnets:[]}:{securityGroups:0===k.length&&a===i.JobsView.CreateForm?[]:Ne(m.runtimeEnvironmentParameters,t.auto_detected_config,a,"vpc_security_group_ids"),subnets:Ne(m.runtimeEnvironmentParameters,t.auto_detected_config,a,"vpc_subnets")}),[]),x=(0,n.useMemo)((()=>((e,t)=>{if(t===i.JobsView.JobDetail||t===i.JobsView.JobDefinitionDetail){if(e)return e.sm_init_script}else if(t===i.JobsView.CreateForm&&e&&"sm_init_script"in e)return e.sm_init_script;return""})(m.runtimeEnvironmentParameters,a)),[]),w=(0,n.useMemo)((()=>(e=>{const t=[];if(e)for(const r in e)if(!De.has(r)){const n={key:r,value:e[r]};t.push(n)}return t})(m.runtimeEnvironmentParameters)),[]),C=(0,n.useMemo)((()=>Fe(m.runtimeEnvironmentParameters,a,"sm_output_kms_key")),[]),P=(0,n.useMemo)((()=>Fe(m.runtimeEnvironmentParameters,a,"sm_volume_kms_key")),[]),M=(0,n.useMemo)((()=>!1),[]),[T,I]=(0,n.useState)({sm_lcc_init_script_arn:b.selectedLccValue||"",role_arn:g||"",vpc_security_group_ids:S.securityGroups||[],vpc_subnets:S.subnets||[],s3_input:h||"",s3_input_account_id:"",s3_output:f||"",s3_output_account_id:"",sm_kernel:"",sm_image:"",sm_init_script:x||"",sm_output_kms_key:C||"",sm_volume_kms_key:P||"",max_retry_attempts:y,max_run_time_in_seconds:j,enable_network_isolation:E}),[N,J]=(0,n.useState)({...T,sm_output_kms_key:"",sm_volume_kms_key:""});(0,n.useEffect)((()=>{const e=(e=>e&&0===e.length?`${Ee.RequiresPrivateSubnet} ${Ee.NoPrivateSubnetsInSageMakerDomain}`:"")(k),t=(r=S.subnets)&&0===r.length?`${Ee.RequiresPrivateSubnet} ${Ee.NoPrivateSubnetsInSageMakerDomain}. ${Ee.YouMayChooseOtherSubnets}`:"";var r;const n={...s,roleError:je(g),s3InputFolderError:_e(h),s3OutputFolderError:_e(f),environmentsStillLoading:"",kernelsStillLoading:"",subnetError:M&&(e||t)||""};u(n)}),[]);const[V,F]=(0,n.useState)();(0,n.useEffect)((()=>{(async function(e){return(await e.get("@amzn/sagemaker-studio-jupyter-scheduler:advanced-options","advancedOptions")).composite})(r).then((e=>{F(e)}))}),[]),(0,n.useEffect)((()=>{var e,t,r,n,o,a;let i={},l={},c={};const m=null!==(e=null==V?void 0:V.enable_network_isolation)&&void 0!==e&&e;i={...i,enable_network_isolation:m};const d=null!==(t=null==V?void 0:V.role_arn)&&void 0!==t?t:"";d&&d!==g&&(i={...i,role_arn:d},l={...l,roleError:je(d)});const p=null!==(r=null==V?void 0:V.s3_input)&&void 0!==r?r:"";p&&p!==h&&(i={...i,s3_input:p},l={...l,s3InputFolderError:_e(p)});const b=null!==(n=null==V?void 0:V.s3_output)&&void 0!==n?n:"";b&&b!==f&&(i={...i,s3_output:b},l={...l,s3OutputFolderError:_e(b)});const y=null!==(o=null==V?void 0:V.sm_output_kms_key)&&void 0!==o?o:"";y&&y!==C&&(c={...c,sm_output_kms_key:y});const E=null!==(a=null==V?void 0:V.sm_volume_kms_key)&&void 0!==a?a:"";E&&E!==P&&(c={...c,sm_volume_kms_key:E}),c={...i,...c},Object.keys(i).length>0&&!v&&J({...N,...i}),Object.keys(c).length>0&&I({...T,...c}),Object.keys(l).length>0&&u({...s,...l})}),[V]);const[O,A]=(0,n.useState)(w),[R,L]=(0,n.useState)(M),$=(0,n.useMemo)((()=>{const e={};return null==O||O.map((t=>{const{key:r,value:n}=t;0!==r.trim().length&&0!==n.trim().length&&(e[r]=n)})),e}),[O]);return(0,n.useEffect)((()=>{var e,t;const r=(null===(e=N.vpc_security_group_ids)||void 0===e?void 0:e.join(","))||"",n=(null===(t=N.vpc_subnets)||void 0===t?void 0:t.join(","))||"";d({...m,runtimeEnvironmentParameters:{...N,vpc_security_group_ids:r,vpc_subnets:n,...$}})}),[N,$]),o().createElement("div",{className:D(v)},o().createElement(st,{isDisabled:v,formState:N,setFormState:J,formErrors:s,setFormErrors:u,...e}),o().createElement(Te,{isDisabled:v,formState:N,setFormState:J,handleChange:e=>{const t=e.target.name,r=e.target.value;J({...N,[t]:r})},handleNumberValueChange:e=>{const t=e.target.name,r=parseInt(e.target.value);J({...N,[t]:isNaN(r)?"":r})},requestClient:l,formErrors:s,setFormValidationErrors:u,environmentVariables:O,userDefaultValues:T,setEnvironmentVariables:A,lccOptions:b.allLCCOptions,availableSecurityGroups:_,availableSubnets:k,initialSecurityGroups:S.securityGroups,initialSubnets:S.subnets,setSubnets:e=>{console.log("setSubnets called with:",e),J({...N,vpc_subnets:e})},setRoleArn:e=>{J({...N,role_arn:e})},setSecurityGroups:e=>{J({...N,vpc_security_group_ids:e})},onSelectLCCScript:e=>{J({...N,sm_lcc_init_script_arn:e})},isVPCDomain:p===c.VpcOnly,enableVPCSetting:R,setEnableVPCSetting:L}))};var ct=r(2453);function mt(e){return getComputedStyle(document.body).getPropertyValue(e).trim()}function dt(){const e=document.body.getAttribute("data-jp-theme-light");return(0,ct.Z)({spacing:4,components:{MuiButton:{defaultProps:{size:"small"}},MuiFilledInput:{defaultProps:{margin:"dense"}},MuiFormControl:{defaultProps:{margin:"dense",size:"small"}},MuiFormHelperText:{defaultProps:{margin:"dense"}},MuiIconButton:{defaultProps:{size:"small"}},MuiInputBase:{defaultProps:{margin:"dense",size:"small"}},MuiInputLabel:{defaultProps:{margin:"dense"},styleOverrides:{root:{display:"flex",alignItems:"center",color:"var(--jp-ui-font-color0)",gap:"6px"}}},MuiListItem:{defaultProps:{dense:!0}},MuiOutlinedInput:{defaultProps:{margin:"dense"}},MuiFab:{defaultProps:{size:"small"}},MuiAutocomplete:{defaultProps:{componentsProps:{paper:{elevation:4}}}},MuiTable:{defaultProps:{size:"small"}},MuiTextField:{defaultProps:{margin:"dense",size:"small"}},MuiToolbar:{defaultProps:{variant:"dense"}}},palette:{background:{paper:mt("--jp-layout-color1"),default:mt("--jp-layout-color1")},mode:"true"===e?"light":"dark",primary:{main:mt("--jp-brand-color1"),light:mt("--jp-brand-color2"),dark:mt("--jp-brand-color0")},error:{main:mt("--jp-error-color1"),light:mt("--jp-error-color2"),dark:mt("--jp-error-color0")},warning:{main:mt("--jp-warn-color1"),light:mt("--jp-warn-color2"),dark:mt("--jp-warn-color0")},success:{main:mt("--jp-success-color1"),light:mt("--jp-success-color2"),dark:mt("--jp-success-color0")},text:{primary:mt("--jp-ui-font-color1"),secondary:mt("--jp-ui-font-color2"),disabled:mt("--jp-ui-font-color3")}},shape:{borderRadius:2},typography:{fontFamily:mt("--jp-ui-font-family"),fontSize:12,htmlFontSize:16,button:{textTransform:"capitalize"}}})}const pt=({requestClient:e,contentsManager:t,commands:r,jobsView:a,errors:c,handleErrorsChange:g,...f})=>{const{pluginEnvironment:h}=Ce(),[y,E]=(0,n.useState)("");(0,n.useEffect)((()=>{const t={...c,environmentsStillLoading:"EnvironmentsStillLoadingError",kernelsStillLoading:"KernelsStillLoadingError"};g(t),a===i.JobsView.CreateForm?(async()=>{const t=v.URLExt.join(e.baseUrl,"/sagemaker_studio_jupyter_scheduler/advanced_environments"),n=await b.ServerConnection.makeRequest(t,{},e);if(200!==n.status&&h.isLocalJL){const e=(await n.json()).error_code;throw Object.values(s).indexOf(e)>=0&&(async e=>{const t=o().createElement(o().Fragment,null,l.Dialog.awsCredentialsError.body.text.map(((e,t)=>o().createElement("p",{key:t,className:G},((e,t)=>{const r=e.split("%");return o().createElement(o().Fragment,null,r.map((e=>{if(e.startsWith("{")){const[r,...n]=e.replace("{","").split("}"),a=t[r],i=n.join("");return a?o().createElement(o().Fragment,null,o().createElement(A,{key:r,href:a.linkHref,target:F.External},a.linkString),i):o().createElement(o().Fragment,null,e)}return o().createElement(o().Fragment,null,e)})))})(e,l.Dialog.awsCredentialsError.body.links))))),r=new m.Dialog({title:l.Dialog.awsCredentialsError.title,body:t,buttons:[m.Dialog.cancelButton(),m.Dialog.okButton({label:l.Dialog.awsCredentialsError.buttons.enterKeysInTerminal})]});(await r.launch()).button.label===l.Dialog.awsCredentialsError.buttons.enterKeysInTerminal&&e.execute(u)})(r),new Error(n.statusText)}return await n.json()})().then((async e=>{S(!1),_(e)})).catch((e=>{E(e.message)})):S(!1)}),[a,f.model.inputFile]);const[j,_]=(0,n.useState)({}),[k,S]=(0,n.useState)(!0);return y?o().createElement("div",{className:H},y):k?null:a!==i.JobsView.CreateForm||(null==j?void 0:j.auto_detected_config)?o().createElement(d.Z,{theme:dt()},o().createElement(p.StyledEngineProvider,{injectFirst:!0},o().createElement(ut,{executionEnvironments:j,requestClient:e,contentsManager:t,jobsView:a,errors:c,handleErrorsChange:g,...f}))):null},vt={id:"@amzn/sagemaker-studio-scheduler:scheduler",autoStart:!1,requires:[a.ISettingRegistry],provides:i.Scheduler.IAdvancedOptions,activate:(e,t)=>r=>{const n=e.serviceManager.serverSettings,a=new b.ContentsManager;return o().createElement(h.StyledEngineProvider,{injectFirst:!0},o().createElement(we,{app:e},o().createElement(pt,{requestClient:n,contentsManager:a,settingRegistry:t,commands:e.commands,...r})))}};var bt;!function(e){e.eventDetail="eventDetail"}(bt||(bt={}));const gt="NotebookJobs",ft={"org.jupyter.jupyter-scheduler.notebook-header.create-job":`${gt}-CreateJob-FromNotebookHeader`,"org.jupyter.jupyter-scheduler.file-browser.create-job":`${gt}-CreateJob-FromFileBrowser`,"org.jupyter.jupyter-scheduler.launcher.show-jobs":`${gt}-JobsList-OpenFromLauncher`,"org.jupyter.jupyter-scheduler.create-job.options.package_input_folder.check":`${gt}-CreateJob-InputFolderCheck`,"org.jupyter.jupyter-scheduler.create-job.options.package_input_folder.uncheck":`${gt}-CreateJob-InputFolderUncheck`,"org.jupyter.jupyter-scheduler.create-job.create-job":`${gt}-CreateJob-Create`,"org.jupyter.jupyter-scheduler.create-job.cancel":`${gt}-CreateJob-Cancel`,"org.jupyter.jupyter-scheduler.create-job.create-job.success":`${gt}-CreateJob-Success`,"org.jupyter.jupyter-scheduler.create-job.create-job.failure":`${gt}-CreateJob-Failure`,"org.jupyter.jupyter-scheduler.create-job.create-job-definition":`${gt}-CreateJob-CreateJobDefinition`,"org.jupyter.jupyter-scheduler.create-job.create-job-definition.success":`${gt}-CreateJobDefinition-Success`,"org.jupyter.jupyter-scheduler.create-job.create-job-definition.failure":`${gt}-CreateJobDefinition-Failure`,"org.jupyter.jupyter-scheduler.create-job-from-definition.create-job":`${gt}-CreateJobFromDefinition-Create`,"org.jupyter.jupyter-scheduler.create-job-from-definition.create-job.success":`${gt}-CreateJobFromDefinition-Success`,"org.jupyter.jupyter-scheduler.create-job-from-definition.create-job.failure":`${gt}-CreateJobFromDefinition-Failure`,"org.jupyter.jupyter-scheduler.create-job-from-definition.cancel":`${gt}-CreateJobFromDefinition-Cancel`,"org.jupyter.jupyter-scheduler.create-job.job-type.run-now":`${gt}-CreateJobType-RunNow`,"org.jupyter.jupyter-scheduler.create-job.job-type.run-on-schedule":`${gt}-CreateJobType-RunOnSchedule`,"org.jupyter.jupyter-scheduler.create-job.advanced-options.expand":`${gt}-CreateJob-ExpandAdvancedOptions`,"org.jupyter.jupyter-scheduler.create-job.advanced-options.collapse":`${gt}-CreateJob-CollapseAdvancedOptions`,"org.jupyter.jupyter-scheduler.jobs-list.reload":`${gt}-JobsList-Reload`,"org.jupyter.jupyter-scheduler.jobs-definition-list.reload":`${gt}-JobsDefinitionList-Reload`,"org.jupyter.jupyter-scheduler.jobs-list.open-input-file":`${gt}-JobsList-OpenInputFile`,"org.jupyter.jupyter-scheduler.jobs-list.open-output-file":`${gt}-JobsList-OpenOutputFile`,"org.jupyter.jupyter-scheduler.job-list.stop-confirm":`${gt}-JobsList-StopConfirm`,"org.jupyter.jupyter-scheduler.jobs-list.download":`${gt}-JobsList-Download`,"org.jupyter.jupyter-scheduler.jobs-list.open-detail":`${gt}-JobsList-OpenDetail`,"org.jupyter.jupyter-scheduler.jobs-list.delete":`${gt}-JobsList-Delete`,"org.jupyter.jupyter-scheduler.jobs-list.stop":`${gt}-JobsList-Stop`,"org.jupyter.jupyter-scheduler.job-definition-list.open-detail":`${gt}-JobsDefinitionList-OpenDetail`,"org.jupyter.jupyter-scheduler.job-definition-list.pause":`${gt}-JobsDefinitionList-Pause`,"org.jupyter.jupyter-scheduler.job-definition-list.resume":`${gt}-JobsDefinitionList-Resume`,"org.jupyter.jupyter-scheduler.job-definition-list.delete":`${gt}-JobsDefinitionList-Delete`,"org.jupyter.jupyter-scheduler.job-detail.open-input-file":`${gt}-JobsDefinitionList-OpenInputFile`,"org.jupyter.jupyter-scheduler.job-detail.open-output-file":`${gt}-JobsDefinitionList-OpenOutputFile`,"org.jupyter.jupyter-scheduler.job-detail.delete":`${gt}-JobDetail-Delete`,"org.jupyter.jupyter-scheduler.job-detail.stop":`${gt}-JobDetail-Stop`,"org.jupyter.jupyter-scheduler.job-detail.download":`${gt}-JobDetail-Download`,"org.jupyter.jupyter-scheduler.job-detail.reload":`${gt}-JobDetail-Reload`,"org.jupyter.jupyter-scheduler.job-definition-detail.reload":`${gt}-JobDefinitonDetail-Reload`,"org.jupyter.jupyter-scheduler.job-definition-detail.run":`${gt}-JobDefinitonDetail-Run`,"org.jupyter.jupyter-scheduler.job-definition-detail.pause":`${gt}-JobDefinitonDetail-Pause`,"org.jupyter.jupyter-scheduler.job-definition-detail.resume":`${gt}-JobDefinitonDetail-Resume`,"org.jupyter.jupyter-scheduler.job-definition-detail.edit":`${gt}-JobDefinitonDetail-Edit`,"org.jupyter.jupyter-scheduler.job-definition-detail.delete":`${gt}-JobDefinitonDetail-Delete`,"org.jupyter.jupyter-scheduler.job-definition-edit.save":`${gt}-JobDefinitonDetail-Save`,"org.jupyter.jupyter-scheduler.job-definition-edit.cancel":`${gt}-JobDefinitonEdit-Cancel`},ht=async e=>{var t;let r;const n=null!==(t=ft[e.body.name])&&void 0!==t?t:e.body.name;r=e.body.detail?JSON.stringify({name:n,error:e.body.detail}):n,window&&window.panorama&&window.panorama("trackCustomEvent",{eventType:bt.eventDetail,eventDetail:r,eventContext:gt,timestamp:e.timestamp.getTime()})},yt=[vt,{id:"@amzn/sagemaker-studio-scheduler:schedulerTelemetry",autoStart:!0,provides:i.Scheduler.TelemetryHandler,activate:e=>ht}]}}]);