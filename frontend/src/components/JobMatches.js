import React from 'react';

const JobMatches = ({ matches, cvData }) => {
  const getMatchScoreClass = (score) => {
    if (score >= 80) return 'bg-green-100 text-green-800';
    if (score >= 60) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  const getMatchScoreLabel = (score) => {
    if (score >= 80) return 'Excellent Match';
    if (score >= 60) return 'Good Match';
    if (score >= 40) return 'Fair Match';
    return 'Low Match';
  };

  return (
    <div>
      {matches && matches.length > 0 ? (
        <div className="space-y-6">
          {matches.map((job, index) => (
            <div key={job.id || index}>
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex justify-between items-start mb-4">
                <div className="flex-1">
                  <h4 className="text-xl font-semibold text-gray-800 mb-2">
                    {job.job_title || 'Job Title Not Available'}
                  </h4>
                  <p className="text-gray-600 mb-2">
                    {job.company || 'Company Not Specified'}
                  </p>
                </div>
                
                <div className="text-right">
                  <div className={`inline-flex px-3 py-1 rounded-full text-sm font-medium ${getMatchScoreClass(job.match_score)}`}>
                    {job.match_score}% Match
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    {getMatchScoreLabel(job.match_score)}
                  </p>
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-4 mb-4 text-sm text-gray-600">
                <div>
                  <strong>Location:</strong> {job.location || 'Not specified'}
                </div>
                
                {job.salary_range && (
                  <div>
                    <strong>Salary:</strong> {job.salary_range}
                  </div>
                )}
              </div>

              <div className="mb-4">
                <h5 className="font-medium text-gray-800 mb-2">Description:</h5>
                <p className="text-gray-600 text-sm leading-relaxed">
                  {job.description || 'No description available'}
                </p>
              </div>

              {job.required_skills && (
                <div className="mb-4">
                  <h5 className="font-medium text-gray-800 mb-2">Required Skills:</h5>
                  <div className="flex flex-wrap gap-2">
                    {job.required_skills.split(',').map((skill, skillIndex) => (
                      <span
                        key={skillIndex}
                        className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-xs whitespace-nowrap"
                      >
                        {skill.trim()}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              <div className="grid md:grid-cols-2 gap-4 text-sm text-gray-600 mb-4">
                {job.experience_level && (
                  <div>
                    <strong>Experience Level:</strong> {job.experience_level}
                  </div>
                )}
                
                {job.education_requirements && (
                  <div>
                    <strong>Education:</strong> {job.education_requirements}
                  </div>
                )}
              </div>
              </div>
              {index < matches.length - 1 && (
                <div className="mt-6 mb-6">
                  <div style={{backgroundColor: '#10412A', height: '4px', width: '100%'}}></div>
                </div>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <div className="bg-white p-8 rounded-lg shadow">
            <h3 className="text-lg font-medium text-gray-600 mb-2">
              No Job Matches Found
            </h3>
            <p className="text-gray-500">
              We couldn't find any matching job opportunities at the moment.
              Try uploading a different CV or check back later.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default JobMatches;
