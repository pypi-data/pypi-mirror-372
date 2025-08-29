(context) => {
  const getFamilyId = () => {
    const sample_ids = [];
    for (const sample of context.samples) {
      if (sample.family_id) {
        return sample.family_id;
      } else {
        sample_ids.push(sample.id);
      }
    }
    return sample_ids.sort().join('__');
  };

  if (!context.samples) {
    throw new Error('Samples are required for this transformation');
  }
  if (context.workflow_params['HumanWGS_wrapper.family']?.samples?.length > 0) {
    return {}
  }

  const backend = context.workflow_params['HumanWGS_wrapper.backend'];

  return {
    workflow_params: {
      'HumanWGS_wrapper.family': {
        family_id: context.workflow_params['HumanWGS_wrapper.family']?.family_id ?? getFamilyId(),
        samples: context.samples?.map(sample => {
          return {
            sample_id: sample.id,
            hifi_reads: sample.files.map(sampleFile => {

              if (backend === "Azure") {
                let uri = sampleFile.path;
                // Remove the "https://" prefix
                if (uri.startsWith("https://")) {
                  uri = uri.slice(8);
                }

                // Split by "/" to extract components
                const parts = uri.split("/");

                // Extract storage account from the first part (hostname)
                const storageAccount = parts[0].split(".")[0];

                // The rest are: container and path
                const container = parts[1];
                const pathParts = parts.slice(2).join("/");

                // Construct the result
                return "/" + storageAccount + "/" + container + "/" + pathParts;
              } else {
                return sampleFile.path;
              }
            }),
            father_id: sample.father_id,
            mother_id: sample.mother_id,
            sex: ["FEMALE", "MALE"].includes(sample.sex) ? sample.sex : null,
            affected: sample.affected ?? false
          }
        }),
      },
    },
    workflow_engine_parameters: backend === "AWS-HealthOmics" ? { ...context.workflow_engine_parameters, storage_type: "DYNAMIC" } : context.workflow_engine_parameters
  }
}
